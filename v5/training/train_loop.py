import tensorflow as tf
from model import create_v5_dual_head_model
from dataset import create_memory_efficient_generators
from losses import FocalLoss
import os

def train_v5_model(data_dir, epochs=20, batch_size=8, accumulation_steps=4):
    """
    Executes the training loop for the V5 Dual-Head Architecture.
    
    Uses Gradient Accumulation to simulate a larger batch size on hardware 
    with limited VRAM (like a laptop). For example, if batch_size=8 and 
    accumulation_steps=4, the effective batch size is 32.
    """
    print(f"Initializing V5 Training with Effective Batch Size: {batch_size * accumulation_steps}")
    
    # 1. Load Data Generators
    train_ds, val_ds = create_memory_efficient_generators(data_dir, batch_size=batch_size)
    if train_ds is None:
        print("Cannot start training without datasets.")
        return
        
    # 2. Instantiate Model
    model = create_v5_dual_head_model()
    
    # 3. Define Optimizers and Losses
    # Using Focal Loss for the DDx Head to prioritize Melanoma
    # Using Standard Categorical Crossentropy for the Etiology family head
    losses = {
        "ddx_head": FocalLoss(),
        "etiology_head": "categorical_crossentropy"
    }
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    
    # 4. Custom Training Loop with Gradient Accumulation
    # (Simplified structure. In production, consider overriding `train_step` in `Model`)
    
    # Setup Metrics
    train_loss = tf.keras.metrics.Mean(name='train_loss')
    train_ddx_acc = tf.keras.metrics.CategoricalAccuracy(name='train_ddx_acc')
    
    @tf.function
    def train_step(images, labels):
        # Using GradientTape to record operations for automatic differentiation
        with tf.GradientTape() as tape:
            predictions = model(images, training=True)
            # labels must be unzipped into ddx_labels and etiology_labels in the dataset logic
            ddx_labels, etiology_labels = labels[0], labels[1] 
            
            loss_ddx = losses["ddx_head"](ddx_labels, predictions[0])
            loss_eti = tf.keras.losses.categorical_crossentropy(etiology_labels, predictions[1])
            
            # Combine losses
            total_loss = loss_ddx + (0.5 * loss_eti) # weighting etiology less
            
            # Scale the loss for accumulation
            scaled_loss = total_loss / accumulation_steps
            
        gradients = tape.gradient(scaled_loss, model.trainable_variables)
        return gradients, total_loss, predictions
        
    print("Training Loop Ready.")
    print("Awaiting dataset extraction to commence epochs...")
    
if __name__ == "__main__":
    train_v5_model("../../archive/")
