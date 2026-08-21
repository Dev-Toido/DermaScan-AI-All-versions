import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import EfficientNetB4

def create_v5_dual_head_model(input_shape=(380, 380, 3), num_ddx_classes=8, num_etiology_classes=4):
    """
    Creates the V5 Dual-Head Architecture for DermaScan AI.
    
    Heads:
    1. Clinical DDx Head: Top 3 Differential Diagnosis (e.g. Melanoma, BCC, etc.)
    2. Etiology Head: Broad categories (Melanocytic, Keratinocytic, Vascular, Inflammatory)
    """
    # Base Model (Pre-trained on ImageNet)
    base_model = EfficientNetB4(
        include_top=False, 
        weights='imagenet', 
        input_shape=input_shape
    )
    
    # Freeze the base model for initial training (we will fine-tune later)
    base_model.trainable = False

    inputs = tf.keras.Input(shape=input_shape)
    
    # Augmentation block
    x = layers.RandomFlip("horizontal_and_vertical")(inputs)
    x = layers.RandomRotation(0.2)(x)
    
    x = base_model(x, training=False)
    
    # Soft Attention Block (focus on the lesion, not the background)
    attention = layers.Conv2D(1, (1, 1), padding='same', activation='sigmoid')(x)
    x = layers.Multiply()([x, attention])
    
    # Global Pooling
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    
    # Shared Dense Layer
    shared = layers.Dense(512, activation='relu')(x)
    shared = layers.BatchNormalization()(shared)
    shared = layers.Dropout(0.3)(shared)
    
    # ---------------------------------------------------------
    # HEAD 1: Clinical DDx Head (8 specific disease classes)
    # ---------------------------------------------------------
    ddx_out = layers.Dense(
        num_ddx_classes, 
        activation='softmax', 
        name='ddx_head'
    )(shared)
    
    # ---------------------------------------------------------
    # HEAD 2: Etiology Category Head (4 broad family classes)
    # ---------------------------------------------------------
    etiology_out = layers.Dense(
        num_etiology_classes, 
        activation='softmax', 
        name='etiology_head'
    )(shared)
    
    # Construct Dual-Head Model
    model = Model(inputs=inputs, outputs=[ddx_out, etiology_out], name="DermaScan_V5_DualHead")
    return model

if __name__ == "__main__":
    # Quick sanity check
    model = create_v5_dual_head_model()
    model.summary()
