import os
import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
from dataset_multimodal import create_dataset_from_df
from model_multimodal import create_v5_multimodal_model
from losses import FocalLoss

def train():
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    
    csv_path = "../data_preparation/train_mapped.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find {csv_path}")
        
    df = pd.read_csv(csv_path)
    print(f"Total dataset size: {len(df)}")
    
    # 1. First split: 80% for Base Models, 20% for Meta-Learner holdout
    # We save the holdout set for later!
    df_base, df_meta = train_test_split(df, test_size=0.2, random_state=42, stratify=df['diagnosis'])
    
    # Save the meta holdout set for the metalearner training script
    df_meta.to_csv("meta_holdout.csv", index=False)
    print(f"Saved {len(df_meta)} samples for Meta-Learner holdout.")
    
    # 2. Second split: split the Base dataset into Train/Val for Model B
    df_train, df_val = train_test_split(df_base, test_size=0.15, random_state=42, stratify=df_base['diagnosis'])
    print(f"Model B - Train: {len(df_train)}, Val: {len(df_val)}")
    
    # 3. Create tf.data datasets
    train_ds = create_dataset_from_df(df_train, batch_size=16, is_training=True, mask_prob=0.3)
    val_ds = create_dataset_from_df(df_val, batch_size=16, is_training=False, mask_prob=0.0)
    
    # 4. Build Model
    model = create_v5_multimodal_model()
    
    # 5. Compile Model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss={
            'ddx_head': FocalLoss(gamma=2.0),
            'etiology_head': 'categorical_crossentropy'
        },
        loss_weights={
            'ddx_head': 1.0,
            'etiology_head': 0.3
        },
        metrics={
            'ddx_head': ['accuracy', tf.keras.metrics.AUC(name='auc')],
            'etiology_head': ['accuracy']
        }
    )
    
    # 6. Callbacks
    os.makedirs('checkpoints', exist_ok=True)
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath='checkpoints/best_model_multimodal.h5',
            monitor='val_ddx_head_auc',
            save_best_only=True,
            save_weights_only=True,
            mode='max',
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_ddx_head_auc',
            patience=5,
            restore_best_weights=True,
            mode='max'
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # 7. Train
    print("Starting Training for Model B (Multimodal Expert)...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=30,
        callbacks=callbacks
    )
    print("Training Complete. Best weights saved to checkpoints/best_model_multimodal.h5")

if __name__ == "__main__":
    train()
