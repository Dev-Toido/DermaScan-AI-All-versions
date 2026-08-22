import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from model import create_v5_dual_head_model
from custom_model import GradientAccumulationModel
from model_multimodal import create_v5_multimodal_model, create_v5_meta_learner
from dataset_multimodal import encode_metadata, get_image_path

def load_image(image_path, img_size=(380, 380)):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.ensure_shape(img, [None, None, 3])
    img = tf.image.resize(img, img_size)
    return tf.expand_dims(img, axis=0) # Add batch dimension

def generate_oof_features():
    print("Generating OOF Features using Model A and Model B...")
    df = pd.read_csv("meta_holdout.csv")
    df['full_path'] = df.apply(lambda row: get_image_path(row, base_archive_path="../../archive"), axis=1)
    
    # Load Models
    base_a = create_v5_dual_head_model()
    model_a = GradientAccumulationModel(inputs=base_a.inputs, outputs=base_a.outputs, accumulation_steps=4)
    import tensorflow as tf
    # We MUST initialize the variables before loading weights!
    model_a.grad_accumulator = [
        tf.Variable(tf.zeros_like(var), trainable=False) 
        for var in model_a.trainable_variables
    ]
    model_a.load_weights('checkpoints/best_model.keras')

    
    model_b = create_v5_multimodal_model()
    model_b.load_weights('checkpoints/best_model_multimodal.h5')
    
    diag_map = {'mel':0, 'nv':1, 'bcc':2, 'ak':3, 'bkl':4, 'df':5, 'vasc':6, 'scc':7, 'unk':8}
    
    all_features = []
    all_ddx_labels = []
    all_eti_labels = []
    
    for _, row in tqdm(df.iterrows(), total=len(df)):
        img = load_image(row['full_path'])
        
        # 1. Get Model A predictions
        ddx_A, eti_A = model_a.predict(img, verbose=0)
        
        # 2. Get Model B predictions
        # For OOF generation, we do not mask metadata (simulate real world)
        meta_vec = encode_metadata(row['age'], row['sex'], row['site'], is_missing=False)
        meta_vec_batch = np.expand_dims(meta_vec, axis=0)
        ddx_B, eti_B = model_b.predict([img, meta_vec_batch], verbose=0)
        
        # 3. Concatenate all features
        # Flatten and combine: 10 + 10 + 4 + 4 + 14 = 42
        fused = np.concatenate([
            ddx_A.flatten(), 
            ddx_B.flatten(), 
            eti_A.flatten(), 
            eti_B.flatten(), 
            meta_vec
        ])
        
        all_features.append(fused)
        
        # 4. Extract Ground Truth
        ddx_idx = diag_map.get(str(row['diagnosis']).lower(), 9)
        all_ddx_labels.append(ddx_idx)
        all_eti_labels.append(row['etiology_family'])
        
    X = np.array(all_features)
    y_ddx = np.array(all_ddx_labels)
    y_eti = np.array(all_eti_labels)
    
    # Save to disk
    np.savez('oof_features.npz', X=X, y_ddx=y_ddx, y_eti=y_eti)
    print(f"Saved {len(X)} OOF features to oof_features.npz")

def train_metalearner():
    print("Training Meta-Learner...")
    if not os.path.exists('oof_features.npz'):
        generate_oof_features()
        
    data = np.load('oof_features.npz')
    X = data['X']
    y_ddx = tf.keras.utils.to_categorical(data['y_ddx'], num_classes=10)
    y_eti = tf.keras.utils.to_categorical(data['y_eti'], num_classes=4)
    
    # Split into Train/Val for Meta-Learner
    X_train, X_val, y_ddx_train, y_ddx_val, y_eti_train, y_eti_val = train_test_split(
        X, y_ddx, y_eti, test_size=0.15, random_state=42
    )
    
    model = create_v5_meta_learner()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )
    
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath='checkpoints/best_model_metalearner.h5',
            monitor='val_ddx_head_auc',
            save_best_only=True,
            save_weights_only=True,
            mode='max'
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_ddx_head_auc',
            patience=15,
            restore_best_weights=True,
            mode='max'
        )
    ]
    
    model.fit(
        X_train,
        {'ddx_head': y_ddx_train, 'etiology_head': y_eti_train},
        validation_data=(X_val, {'ddx_head': y_ddx_val, 'etiology_head': y_eti_val}),
        epochs=100,
        batch_size=32,
        callbacks=callbacks
    )
    print("Meta-Learner Training Complete!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--generate':
        generate_oof_features()
    else:
        train_metalearner()
