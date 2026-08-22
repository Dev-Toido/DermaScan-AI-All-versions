import tensorflow as tf
import numpy as np
import cv2
import base64

def generate_gradcam(model, image_array, class_idx):
    """
    Generate Grad-CAM heatmap for a single-input Image model.
    """
    # Target the 'multiply' layer, but instead of using its output (which is heavily masked),
    # grab its FIRST input tensor. This gives us the raw EfficientNetB4 feature map in the OUTER graph,
    # preventing the 'Graph disconnected' ValueError when building the Grad-CAM sub-model.
    conv_output = None
    for layer in reversed(model.layers):
        if layer.name == 'multiply':
            if hasattr(layer, 'input') and isinstance(layer.input, list) and len(layer.input) > 0:
                conv_output = layer.input[0]
            break
            
    if conv_output is None:
        # Fallback to the last 4D layer's output
        for layer in reversed(model.layers):
            if hasattr(layer, 'output_shape') and isinstance(layer.output_shape, tuple) and len(layer.output_shape) == 4:
                conv_output = layer.output
                break
                
    if conv_output is None:
        raise ValueError("Could not find a valid 4D convolutional tensor for Grad-CAM.")
        
    # We want gradients of the DDX head (which is the first output)
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[conv_output, model.output[0]] # index 0 is ddx_head
    )
    
    # img_input is already (1, 380, 380, 3) in main.py, but just in case:
    if len(image_array.shape) == 3:
        img_input = np.expand_dims(image_array, axis=0)
    else:
        img_input = image_array
        
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_input)
        top_class_score = predictions[:, class_idx]
    
    grads = tape.gradient(top_class_score, conv_outputs)
    
    pooled_grads = tf.reduce_mean(grads, axis=(1, 2))  
    
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads[0], conv_outputs), axis=-1)
    
    heatmap = tf.maximum(heatmap, 0)
    
    max_val = tf.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
        
    heatmap = heatmap.numpy()
    
    # Resize to match original image array size
    if len(image_array.shape) == 4:
        image_array = image_array[0]
        
    target_size = (image_array.shape[1], image_array.shape[0])
    heatmap = cv2.resize(heatmap, target_size, interpolation=cv2.INTER_CUBIC)
    heatmap = np.clip(heatmap, 0.0, 1.0)
    
    return heatmap

def overlay_heatmap(image_array, heatmap, alpha=0.5):
    """
    Superimpose the heatmap on the original image and return Base64.
    image_array should be normalized (0 to 1).
    """
    # Remove batch dim if present
    if len(image_array.shape) == 4:
        image_array = image_array[0]
        
    # Denormalize image_array to [0, 255] if it's not already
    if np.max(image_array) <= 1.0 or np.min(image_array) < 0:
        # EfficientNet preprocess_input might make it [-1, 1], but in our main.py it's just raw resized
        # Wait, in main.py, img_resized is [0,255]. Then we apply preprocess_input!
        # preprocess_input for efficientnet doesn't change [0,255] for B0-B7 in keras applications, but let's be safe.
        pass
        
    img_uint8 = np.uint8(np.clip(255 * image_array, 0, 255))
    
    heatmap_colored = np.uint8(255 * heatmap)
    heatmap_colored_bgr = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored_bgr, cv2.COLOR_BGR2RGB)
    
    superimposed_rgb = cv2.addWeighted(img_uint8, 1 - alpha, heatmap_colored_rgb, alpha, 0)
    
    # Convert to Base64
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(superimposed_rgb, cv2.COLOR_RGB2BGR))
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"
