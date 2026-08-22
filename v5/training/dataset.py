import tensorflow as tf
import pandas as pd
import os

def load_and_preprocess_image(image_path, ddx_label, eti_label, img_size=(380, 380)):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.ensure_shape(img, [None, None, 3])
    img = tf.image.resize(img, img_size)
    
    # 9 core diagnoses + 1 'Unknown' (10 classes)
    ddx_one_hot = tf.one_hot(ddx_label, depth=10)
    # 4 Etiology families
    eti_one_hot = tf.one_hot(eti_label, depth=4)
    
    # Keras multi-output expects a tuple of labels
    return img, (ddx_one_hot, eti_one_hot)

def get_image_path(row, base_archive_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "archive"))):
    """Constructs the exact absolute/relative path based on the dataset source."""
    if row['source'] == 'ISIC':
        return os.path.join(base_archive_path, 'ISIC', 'ISIC_2019_Training_Input', 'ISIC_2019_Training_Input', f"{row['image_id']}.jpg")
    elif row['source'] == 'Diverse':
        # Ensure DDI ID is padded to 6 digits if it's an integer
        img_id = str(row['image_id']).zfill(6)
        return os.path.join(base_archive_path, 'DDI_Dataset', f"{img_id}.png")
    else:
        # Fallback
        return os.path.join(base_archive_path, f"{row['image_id']}.jpg")

def create_csv_dataset_generator(csv_path, batch_size=16, img_size=(380, 380), is_training=True):
    """
    Creates a streaming tf.data.Dataset directly from the mapped CSV files.
    This prevents memory crashes (OOM) and avoids having to physically move 25,000 images!
    """
    if not os.path.exists(csv_path):
        print(f"WARNING: CSV not found at {csv_path}")
        return None
        
    df = pd.read_csv(csv_path)
    
    # Construct the full image paths
    # Assuming this script is run from `v5/training/`, so `archive/` is at `../../archive/`
    df['full_path'] = df.apply(lambda row: get_image_path(row, base_archive_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "archive"))), axis=1)
    
    # Create the tf.data dataset from the lists of paths and labels
    # Need to numericalize diagnosis strings for DDx head (simplified to 0-9)
    # 0: MEL, 1: NV, 2: BCC, 3: AK, 4: BKL, 5: DF, 6: VASC, 7: SCC, 8: UNK, 9: Other
    diag_map = {'mel':0, 'nv':1, 'bcc':2, 'ak':3, 'bkl':4, 'df':5, 'vasc':6, 'scc':7, 'unk':8}
    df['ddx_idx'] = df['diagnosis'].str.lower().map(diag_map).fillna(9).astype(int)
    
    paths = df['full_path'].values
    ddx_labels = df['ddx_idx'].values
    eti_labels = df['etiology_family'].values
    
    ds = tf.data.Dataset.from_tensor_slices((paths, ddx_labels, eti_labels))
    
    if is_training:
        ds = ds.shuffle(buffer_size=10000, seed=42)
        
    AUTOTUNE = tf.data.AUTOTUNE
    
    ds = ds.map(
        lambda p, d, e: load_and_preprocess_image(p, d, e, img_size=img_size), 
        num_parallel_calls=AUTOTUNE
    )
    
    # Batch and prefetch
    ds = ds.batch(batch_size).prefetch(buffer_size=AUTOTUNE)
    
    return ds


def create_replay_buffer_generator(standard_csv_path, hard_csv_path, batch_size=16, img_size=(380, 380)):
    """
    Continuous Learning Loop implementation.
    Mixes standard historical dataset with hard examples submitted by doctors.
    Enforces a 90/10 split to prevent catastrophic forgetting.
    """
    # Create the standard dataset generator (unbatched for sampling)
    standard_ds = create_csv_dataset_generator(standard_csv_path, batch_size=batch_size, img_size=img_size, is_training=True)
    if standard_ds is not None:
        standard_ds = standard_ds.unbatch()
    
    AUTOTUNE = tf.data.AUTOTUNE
    
    if not os.path.exists(hard_csv_path):
        print(f"No hard examples found at {hard_csv_path}. Using standard dataset only.")
        return standard_ds.batch(batch_size).prefetch(AUTOTUNE) if standard_ds else None
        
    df_hard = pd.read_csv(hard_csv_path)
    if len(df_hard) == 0:
        return standard_ds.batch(batch_size).prefetch(AUTOTUNE) if standard_ds else None
        
    print(f"✅ Found {len(df_hard)} hard examples. Activating Replay Buffer (90/10 mix).")
    
    # Construct paths for hard examples
    base_dir = os.path.dirname(__file__)
    df_hard['full_path'] = df_hard['image_id'].apply(lambda x: os.path.abspath(os.path.join(base_dir, "..", "data_preparation", "hard_examples", f"{x}.jpg")))
    
    diag_map = {'mel':0, 'nv':1, 'bcc':2, 'ak':3, 'bkl':4, 'df':5, 'vasc':6, 'scc':7, 'unk':8}
    df_hard['ddx_idx'] = df_hard['diagnosis'].str.lower().map(diag_map).fillna(9).astype(int)
    
    # Map etiology (Melanocytic:0, Epithelial:1, Vascular:2, Other:3)
    etiology_map = {0:0, 1:0, 2:1, 3:1, 4:1, 7:1, 6:2, 5:3, 8:3, 9:3}
    df_hard['etiology_family'] = df_hard['ddx_idx'].map(etiology_map).fillna(3).astype(int)
    
    paths = df_hard['full_path'].values
    ddx_labels = df_hard['ddx_idx'].values
    eti_labels = df_hard['etiology_family'].values
    
    hard_ds = tf.data.Dataset.from_tensor_slices((paths, ddx_labels, eti_labels))
    hard_ds = hard_ds.shuffle(1000).repeat()
    
    hard_ds = hard_ds.map(
        lambda p, d, e: load_and_preprocess_image(p, d, e, img_size=img_size), 
        num_parallel_calls=AUTOTUNE
    )
    
    # Sample from both datasets with 90/10 split
    replay_ds = tf.data.Dataset.sample_from_datasets([standard_ds.repeat(), hard_ds], weights=[0.90, 0.10])
    
    return replay_ds.batch(batch_size).prefetch(buffer_size=AUTOTUNE)

if __name__ == "__main__":
    print("Testing the new CSV Streaming Pipeline...")
    
    # The script is usually run from v5/training, so the CSV is in ../data_preparation/
    train_ds = create_csv_dataset_generator("../data_preparation/train_mapped.csv", batch_size=4)
    
    if train_ds:
        # Pull exactly 1 batch to verify it doesn't crash
        for images, labels in train_ds.take(1):
            print(f"✅ SUCCESS! Loaded a batch of images.")
            print(f" - Image batch shape: {images.shape}")
            print(f" - Label batch shape: {labels.shape}")
            break
