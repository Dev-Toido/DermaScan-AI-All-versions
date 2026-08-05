import tensorflow as tf
import numpy as np
import cv2

def generate_gradcam(model, image_array, class_idx, meta_features=None):
    """
    Generate Grad-CAM heatmap for a two-input model (image + metadata).
    """
    # 1. Identify the Final Conv Layer dynamically
    conv_layer = None
    try:
        conv_layer = model.get_layer('top_conv')
    except ValueError:
        pass
        
    if conv_layer is None:
        # Search for the absolute final convolutional layer before the GAP layer
        for layer in reversed(model.layers):
            if hasattr(layer, 'output_shape') and isinstance(layer.output_shape, tuple) and len(layer.output_shape) == 4:
                conv_layer = layer
                break
                
    if conv_layer is None:
        raise ValueError("Could not find a valid 4D convolutional layer for Grad-CAM.")
        
    # Build a grad model that outputs both the conv layer activation and the final prediction
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[conv_layer.output, model.output]
    )
    
    # Prepare the inputs
    img_input = np.expand_dims(image_array, axis=0).astype(np.float32)
    
    if meta_features is None:
        meta_input_shape = model.inputs[1].shape[1]
        meta_features = np.zeros((1, meta_input_shape), dtype=np.float32)
    else:
        meta_features = meta_features.astype(np.float32)
    
    # 2. Gradient Calculation
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model([img_input, meta_features])
        top_class_score = predictions[:, class_idx]
    
    grads = tape.gradient(top_class_score, conv_outputs)
    
    # Pool the gradients over the spatial dimensions
    pooled_grads = tf.reduce_mean(grads, axis=(1, 2))  # shape (batch, channels)
    
    # Weight the channels of the conv output by the pooled gradients
    conv_outputs = conv_outputs[0]  # remove batch dimension
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads[0], conv_outputs), axis=-1)
    
    # 3. Heatmap Post-Processing
    # ReLU Activation: ensure we only care about positive influences
    heatmap = tf.maximum(heatmap, 0)
    
    # Normalization: strictly between 0 and 1
    max_val = tf.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
        
    # Convert to numpy and resize to original image array shape perfectly aligned
    heatmap = heatmap.numpy()
    target_size = (image_array.shape[1], image_array.shape[0])
    heatmap = cv2.resize(heatmap, target_size, interpolation=cv2.INTER_CUBIC)
    
    # Clip after cubic interpolation to prevent under/overshoot
    heatmap = np.clip(heatmap, 0.0, 1.0)
    
    return heatmap

def overlay_heatmap(image_array, heatmap, alpha=0.5):
    """
    Superimpose the heatmap on the original image.
    """
    # Convert image to uint8 [0,255]
    img_uint8 = np.uint8(np.clip(255 * image_array, 0, 255))
    
    # Apply a colormap to the heatmap (jet)
    heatmap_colored = np.uint8(255 * heatmap)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    
    # Blend perfectly aligned
    superimposed = cv2.addWeighted(img_uint8, 1 - alpha, heatmap_colored, alpha, 0)
    return superimposed