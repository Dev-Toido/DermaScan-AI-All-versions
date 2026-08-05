import tensorflow as tf
import numpy as np
import cv2

def generate_gradcam(model, image_array, class_idx, meta_features=None):
    """
    Generate Grad-CAM heatmap for a two-input model (image + metadata).
    
    Args:
        model: tf.keras.Model with two inputs [image, metadata]
        image_array: preprocessed image numpy array (H, W, 3)
        class_idx: index of the target class
        meta_features: preprocessed metadata vector shape (1, num_meta) (optional, uses zeros if None)
        
    Returns:
        heatmap: numpy array of shape (H, W) with values in [0,1]
    """
    # Find the last convolutional layer in the image branch (named 'top_conv')
    conv_layer = model.get_layer('top_conv')
    
    # Build a grad model that outputs both the conv layer activation and the final prediction
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[conv_layer.output, model.output]
    )
    
    # Prepare the inputs
    img_input = np.expand_dims(image_array, axis=0).astype(np.float32)
    
    if meta_features is None:
        # Fallback: create a zero metadata vector with correct shape
        meta_input_shape = model.inputs[1].shape[1]  # number of metadata features
        meta_features = np.zeros((1, meta_input_shape), dtype=np.float32)
    else:
        meta_features = meta_features.astype(np.float32)
    
    # Compute gradients of the predicted class score w.r.t. the conv layer output
    with tf.GradientTape() as tape:
        conv_output, predictions = grad_model([img_input, meta_features])
        # We need to watch conv_output to compute gradients
        tape.watch(conv_output)
        # Recompute score after watch? No, we need score from predictions, but the conv_output is already an output.
        # We can instead re-run the model with tape.watch on the conv_output manually? 
        # The above won't work because conv_output is not being watched automatically.
        # Correct approach: we should use the tape to watch the conv_output tensor itself.
        # But conv_output is produced by grad_model, not an input. We need to include the model's forward pass inside the tape, and then compute the gradient of the prediction with respect to the conv_output.
        # We can do:
        #   with tf.GradientTape() as tape:
        #       conv_output, predictions = grad_model([img_input, meta_features])
        #       top_class_score = predictions[:, class_idx]
        #   grads = tape.gradient(top_class_score, conv_output)
        # This works because conv_output is an output of the model, and the tape will track the operations.
    
    # So, correct implementation:
    with tf.GradientTape() as tape:
        conv_output, predictions = grad_model([img_input, meta_features])
        top_class_score = predictions[:, class_idx]
    
    grads = tape.gradient(top_class_score, conv_output)
    
    # Pool the gradients over the spatial dimensions
    pooled_grads = tf.reduce_mean(grads, axis=(1, 2))  # shape (batch, channels)
    
    # Weight the channels of the conv output by the pooled gradients
    conv_output = conv_output[0]  # remove batch dimension
    heatmap = tf.reduce_sum(pooled_grads[0] * conv_output, axis=-1)
    
    # Apply ReLU to keep only positive influence
    heatmap = tf.maximum(heatmap, 0)
    
    # Normalize to [0,1]
    max_val = tf.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    
    # Resize to the original image size (image_array is (H,W,3))
    heatmap = tf.image.resize(heatmap[..., tf.newaxis], image_array.shape[:2])
    heatmap = tf.squeeze(heatmap).numpy()
    
    return heatmap


def overlay_heatmap(image_array, heatmap, alpha=0.5):
    """
    Superimpose the heatmap on the original image.
    
    Args:
        image_array: normalized image (H, W, 3) with values in [0,1]
        heatmap: (H, W) heatmap with values in [0,1]
        alpha: blending factor
    
    Returns:
        superimposed: uint8 image array (H, W, 3) suitable for display
    """
    # Convert image to uint8 [0,255]
    img_uint8 = np.uint8(255 * image_array)
    
    # Apply a colormap to the heatmap (jet)
    heatmap_colored = np.uint8(255 * heatmap)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    
    # Blend
    superimposed = cv2.addWeighted(img_uint8, 1 - alpha, heatmap_colored, alpha, 0)
    return superimposed