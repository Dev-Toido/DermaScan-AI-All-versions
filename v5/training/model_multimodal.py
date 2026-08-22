import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D, Dropout, Concatenate, BatchNormalization, Activation
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50V2

def create_v5_multimodal_model(img_size=(380, 380, 3), metadata_size=14, ddx_classes=10, eti_classes=4):
    """
    Creates Model B (Multimodal Expert).
    Combines ResNet50V2 for image features and an MLP for metadata features.
    """
    # --- Branch 1: Image Processing (ResNet50V2) ---
    img_input = Input(shape=img_size, name='image_input')
    resnet = ResNet50V2(include_top=False, weights='imagenet', input_tensor=img_input)
    
    img_features = GlobalAveragePooling2D()(resnet.output)
    img_features = Dense(256, activation='relu')(img_features)
    img_features = Dropout(0.4)(img_features)
    
    # --- Branch 2: Metadata Processing (MLP) ---
    meta_input = Input(shape=(metadata_size,), name='metadata_input')
    meta_features = Dense(32)(meta_input)
    meta_features = BatchNormalization()(meta_features)
    meta_features = Activation('relu')(meta_features)
    meta_features = Dropout(0.2)(meta_features)
    meta_features = Dense(16, activation='relu')(meta_features)
    
    # --- Fusion ---
    merged = Concatenate()([img_features, meta_features])
    merged = Dense(256, activation='relu')(merged)
    merged = Dropout(0.4)(merged)
    
    # --- Outputs ---
    ddx_out = Dense(ddx_classes, activation='softmax', name='ddx_head', dtype='float32')(merged)
    eti_out = Dense(eti_classes, activation='softmax', name='etiology_head', dtype='float32')(merged)
    
    model = Model(inputs=[img_input, meta_input], outputs=[ddx_out, eti_out], name="V5_Multimodal_Expert")
    return model

def create_v5_meta_learner(ddx_classes=10, eti_classes=4, metadata_size=14):
    """
    Creates Model C (The Converging Meta-Learner).
    Input size = Model A DDX (10) + Model B DDX (10) + Model A Etiology (4) + Model B Etiology (4) + Metadata (14) = 42
    """
    input_size = (ddx_classes * 2) + (eti_classes * 2) + metadata_size
    meta_input = Input(shape=(input_size,), name='meta_learner_input')
    
    x = Dense(64)(meta_input)
    x = BatchNormalization()(x)
    x = Activation('swish')(x)
    x = Dropout(0.4)(x)
    
    x = Dense(32)(x)
    x = BatchNormalization()(x)
    x = Activation('swish')(x)
    x = Dropout(0.3)(x)
    
    # Output predicting the true diagnosis and etiology based on the ensemble inputs
    ddx_out = Dense(ddx_classes, activation='softmax', name='ddx_head', dtype='float32')(x)
    eti_out = Dense(eti_classes, activation='softmax', name='etiology_head', dtype='float32')(x)
    
    model = Model(inputs=meta_input, outputs=[ddx_out, eti_out], name="V5_Meta_Learner")
    return model
