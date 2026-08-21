import tensorflow as tf
import os

def create_memory_efficient_generators(data_dir, batch_size=16, img_size=(380, 380)):
    """
    Creates memory-efficient data generators for laptop-optimized training.
    Uses tf.keras.utils.image_dataset_from_directory which streams images 
    directly from the disk in batches without loading the whole dataset into RAM.
    
    Expected folder structure for `data_dir`:
    data_dir/
      train/
        melanoma/
        basal_cell_carcinoma/
        ...
      val/
        melanoma/
        ...
    """
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    if not os.path.exists(train_dir):
        print(f"WARNING: Data directory {train_dir} does not exist yet. Awaiting dataset download.")
        return None, None
        
    print("Initializing streaming Data Generators...")
    
    # Training Dataset
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        label_mode='categorical',
        batch_size=batch_size,
        image_size=img_size,
        shuffle=True,
        seed=42
    )
    
    # Validation Dataset
    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        label_mode='categorical',
        batch_size=batch_size,
        image_size=img_size,
        shuffle=False
    )
    
    # Optimize for performance (Prefetching allows the CPU to load the next batch 
    # while the GPU is training the current batch)
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    
    return train_ds, val_ds

if __name__ == "__main__":
    # Test script will safely abort if data isn't there yet
    t_ds, v_ds = create_memory_efficient_generators("../../archive/")
    if t_ds:
        print("Data Generators successfully hooked to disk!")
