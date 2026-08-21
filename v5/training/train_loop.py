import tensorflow as tf
from model import create_v5_dual_head_model
from custom_model import GradientAccumulationModel
from dataset import create_csv_dataset_generator
from losses import FocalLoss
import os

def train_v5_model(data_dir, epochs=50, batch_size=8, accumulation_steps=4):
    """
    Executes the training loop for the V5 Dual-Head Architecture using Keras Callbacks.
    Effective Batch Size = 8 * 4 = 32.
    """
    print(f"Initializing V5 Training with Effective Batch Size: {batch_size * accumulation_steps}")
    
    # 1. Load Data Generators
    train_ds = create_csv_dataset_generator(os.path.join(data_dir, "train_mapped.csv"), batch_size=batch_size, is_training=True)
    val_ds = create_csv_dataset_generator(os.path.join(data_dir, "val_mapped.csv"), batch_size=batch_size, is_training=False)
    
    if train_ds is None or val_ds is None:
        print("Cannot start training without datasets.")
        return
        
    # 2. Instantiate Base Model
    base_model = create_v5_dual_head_model()
    
    # Wrap with our Custom Gradient Accumulator
    model = GradientAccumulationModel(
        inputs=base_model.inputs, 
        outputs=base_model.outputs, 
        accumulation_steps=accumulation_steps
    )
    
    # 3. Define Optimizers and Losses
    losses = {
        "ddx_head": FocalLoss(),
        "etiology_head": "categorical_crossentropy"
    }
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    
    # Compile the model
    model.compile(
        optimizer=optimizer,
        loss=losses,
        loss_weights={"ddx_head": 1.0, "etiology_head": 0.5},
        metrics={"ddx_head": "accuracy", "etiology_head": "accuracy"}
    )
    
    # 4. Setup Checkpoints & Callbacks
    checkpoint_dir = "checkpoints"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(checkpoint_dir, "best_model.keras"),
            save_best_only=True,
            monitor="val_loss",
            mode="min",
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        tf.keras.callbacks.TensorBoard(
            log_dir="./logs",
            histogram_freq=1
        )
    ]
    
    print("Beginning Training Epochs...")
    
    # 5. Start Training
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks
    )
    
if __name__ == "__main__":
    train_v5_model("../data_preparation/")
