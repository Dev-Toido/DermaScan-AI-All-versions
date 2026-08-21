import os
# At the very top, after import os
import os
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'
os.environ['TF_XLA_FLAGS'] = '--tf_xla_auto_jit=0'

import tensorflow as tf
# Force minimal GPU usage
tf.config.optimizer.set_jit(False)
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        pass

# Disable mixed precision – use pure float32
tf.keras.mixed_precision.set_global_policy('float32')

# In the create_tf_dataset function, change IMAGE_SIZE to (288, 288)
# In argparse, batch_size default=1
import argparse
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import logging

from model import build_model
from preprocess import create_tf_dataset, IMAGE_SIZE

# Completely disable XLA JIT
tf.config.optimizer.set_jit(False)

# Force TensorFlow to use only the necessary GPU memory
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logging.info("GPU memory growth enabled")
    except RuntimeError as e:
        logging.warning(f"Could not set memory growth: {e}")

# Also set a memory allocator environment
import os
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'

# Configure GPU memory growth to avoid OOM
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logging.info("GPU memory growth enabled")
    except RuntimeError as e:
        logging.warning(f"Could not set memory growth: {e}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_meta_dim(df):
    """Determine metadata column names (all except non-feature columns)."""
    site_cols = [col for col in df.columns if col.startswith('site_')]
    meta_cols = ['age_approx_normalized', 'age_missing', 'sex_encoded'] + site_cols
    return len(meta_cols)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data", help="Path to the data folder")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size (2 is safe for 6GB VRAM)")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    # Enable mixed precision as per project constitution
    tf.keras.mixed_precision.set_global_policy('mixed_float16')
    logging.info(f"Mixed precision policy: {tf.keras.mixed_precision.global_policy().name}")

    out_dir = os.path.join(args.data_dir, "processed")
    image_dir = os.path.join(args.data_dir, "ISIC_2019_Training_Input")
    
    # Load processed splits
    logging.info("Loading processed dataset splits...")
    train_df = pd.read_csv(os.path.join(out_dir, "train.csv"))
    val_df = pd.read_csv(os.path.join(out_dir, "val.csv"))
    test_df = pd.read_csv(os.path.join(out_dir, "test.csv"))
    
    meta_dim = get_meta_dim(train_df)
    logging.info(f"Metadata dimension: {meta_dim}")

    # Build tf.data pipelines
    logging.info("Creating tf.data pipelines...")
    train_ds = create_tf_dataset(train_df, image_dir, batch_size=args.batch_size, is_training=True)
    val_ds = create_tf_dataset(val_df, image_dir, batch_size=args.batch_size, is_training=False)
    test_ds = create_tf_dataset(test_df, image_dir, batch_size=args.batch_size, is_training=False)
    
    # Compute class weights for imbalanced dataset
    labels = train_df['label'].values
    classes = np.unique(labels)
    weights = compute_class_weight('balanced', classes=classes, y=labels)
    class_weight_dict = {cls: weight for cls, weight in zip(classes, weights)}
    logging.info(f"Computed class weights: {class_weight_dict}")

    # Build model
    logging.info("Building model...")
    model = build_model(input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), meta_dim=meta_dim, num_classes=8)
    model.summary(print_fn=logging.info)

    # Compile model
    optimizer = tf.keras.optimizers.Adam(learning_rate=args.lr)
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Callbacks
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath='dermascan_v3_best.keras',
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_accuracy',
            factor=0.5,
            patience=3,
            verbose=1
        ),
        tf.keras.callbacks.CSVLogger('training_log.csv')
    ]

    # Train
    logging.info("Starting training...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        class_weight=class_weight_dict,
        callbacks=callbacks
    )

    # Evaluate on test set
    logging.info("Evaluating on test set...")
    test_loss, test_acc = model.evaluate(test_ds)
    logging.info(f"Test Loss: {test_loss:.4f}")
    logging.info(f"Test Accuracy: {test_acc:.4f}")

    # Generate predictions for report
    logging.info("Generating classification report and confusion matrix...")
    y_true = test_df['label'].values
    
    preds = model.predict(test_ds)
    y_pred = np.argmax(preds, axis=1)

    # Load label names
    with open("preprocessing_objects.pkl", "rb") as f:
        objects = pickle.load(f)
    label_names = objects['label_names']

    report = classification_report(y_true, y_pred, target_names=label_names)
    logging.info("\n" + report)
    
    cm = confusion_matrix(y_true, y_pred)
    logging.info(f"Confusion Matrix:\n{cm}")
    
    with open("test_evaluation.txt", "w") as f:
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\n\nConfusion Matrix:\n")
        f.write(str(cm))
    logging.info("Detailed evaluation saved to test_evaluation.txt")

if __name__ == "__main__":
    main()
