import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB4

def build_model(input_shape=(380, 380, 3), meta_dim=12, num_classes=8):
    """
    Builds the DermaScan AI V3 model fusing image features and metadata.
    
    Args:
        input_shape: Shape of the input image. Default is (380, 380, 3) for EfficientNetB4.
        meta_dim: Dimension of the metadata input vector.
        num_classes: Number of output classes.
        
    Returns:
        A compiled tf.keras.Model
    """
    # --------------------------
    # Image Stream
    # --------------------------
    image_input = layers.Input(shape=input_shape, name="image_input")
    
    base_model = EfficientNetB4(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    # The base model is left unfrozen for fine-tuning
    
    x_img = base_model(image_input)
    x_img = layers.GlobalAveragePooling2D(name="global_average_pooling")(x_img)
    # Outputs a 1792-D image embedding
    
    # --------------------------
    # Metadata Stream
    # --------------------------
    meta_input = layers.Input(shape=(meta_dim,), name="meta_input")
    x_meta = layers.Dense(32, activation='relu', name="meta_dense_1")(meta_input)
    # Outputs a 32-D metadata embedding
    
    # --------------------------
    # Fusion
    # --------------------------
    x_concat = layers.Concatenate(name="fusion_concat")([x_img, x_meta])
    x_concat = layers.Dense(256, activation='relu', name="fusion_dense")(x_concat)
    x_concat = layers.Dropout(0.5, name="fusion_dropout")(x_concat)
    
    # Explicit dtype='float32' ensures numeric stability when using mixed precision ('mixed_float16')
    output = layers.Dense(num_classes, activation='softmax', name="classifier_output", dtype='float32')(x_concat)
    
    model = models.Model(inputs=[image_input, meta_input], outputs=output, name="DermaScan_V3_MultiModal")
    return model
