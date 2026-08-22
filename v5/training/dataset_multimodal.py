import tensorflow as tf
import pandas as pd
import numpy as np
import os

# Define metadata categories
SEX_CATEGORIES = ['male', 'female', 'unknown']
SITE_CATEGORIES = ['posterior torso', 'upper extremity', 'lower extremity', 
                   'head/neck', 'anterior torso', 'oral/genital', 
                   'palms/soles', 'lateral torso', 'unknown']

def encode_metadata(age, sex, site, is_missing=False):
    """Encodes metadata into a 14-dimensional normalized vector."""
    # 1. Age (Normalized, say max age 100)
    # If missing or is_missing flag is true, age = 0
    if is_missing or pd.isna(age) or age < 0:
        age_norm = 0.0
    else:
        age_norm = min(float(age) / 100.0, 1.0)
        
    # 2. Sex (One-hot)
    sex_one_hot = [0.0] * len(SEX_CATEGORIES)
    if is_missing or pd.isna(sex) or sex not in SEX_CATEGORIES:
        sex_idx = SEX_CATEGORIES.index('unknown')
    else:
        sex_idx = SEX_CATEGORIES.index(sex)
    sex_one_hot[sex_idx] = 1.0
    
    # 3. Site (One-hot)
    site_one_hot = [0.0] * len(SITE_CATEGORIES)
    if is_missing or pd.isna(site) or site not in SITE_CATEGORIES:
        site_idx = SITE_CATEGORIES.index('unknown')
    else:
        site_idx = SITE_CATEGORIES.index(site)
    site_one_hot[site_idx] = 1.0
    
    # 4. is_missing flag (1.0 if missing, 0.0 if present)
    missing_flag = [1.0 if is_missing else 0.0]
    
    # Concatenate all features: 1 (age) + 3 (sex) + 9 (site) + 1 (missing flag) = 14 features
    metadata_vector = [age_norm] + sex_one_hot + site_one_hot + missing_flag
    return np.array(metadata_vector, dtype=np.float32)

def load_and_preprocess_multimodal(image_path, metadata_vec, ddx_label, eti_label, img_size=(380, 380)):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.ensure_shape(img, [None, None, 3])
    img = tf.image.resize(img, img_size)
    
    # 9 core diagnoses + 1 'Unknown' (10 classes)
    ddx_one_hot = tf.one_hot(ddx_label, depth=10)
    # 4 Etiology families
    eti_one_hot = tf.one_hot(eti_label, depth=4)
    
    # Yield ((image, metadata), (ddx, eti))
    return (img, metadata_vec), (ddx_one_hot, eti_one_hot)

def get_image_path(row, base_archive_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "archive"))):
    if row['source'] == 'ISIC':
        return os.path.join(base_archive_path, 'ISIC', 'ISIC_2019_Training_Input', 'ISIC_2019_Training_Input', f"{row['image_id']}.jpg")
    elif row['source'] == 'Diverse':
        img_id = str(row['image_id']).zfill(6)
        return os.path.join(base_archive_path, 'DDI_Dataset', f"{img_id}.png")
    else:
        return os.path.join(base_archive_path, f"{row['image_id']}.jpg")

def create_dataset_from_df(df, batch_size=16, img_size=(380, 380), is_training=True, mask_prob=0.2, base_archive_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "archive"))):
    """
    Creates a tf.data.Dataset from a Pandas DataFrame, supporting multimodal inputs.
    """
    # Construct paths
    df['full_path'] = df.apply(lambda row: get_image_path(row, base_archive_path=base_archive_path), axis=1)
    
    # Map diagnosis to index
    diag_map = {'mel':0, 'nv':1, 'bcc':2, 'ak':3, 'bkl':4, 'df':5, 'vasc':6, 'scc':7, 'unk':8}
    df['ddx_idx'] = df['diagnosis'].str.lower().map(diag_map).fillna(9).astype(int)
    
    # Pre-compute metadata vectors
    metadata_vectors = []
    for _, row in df.iterrows():
        # During training, randomly mask metadata with probability `mask_prob`
        is_masked = is_training and (np.random.rand() < mask_prob)
        vec = encode_metadata(row['age'], row['sex'], row['site'], is_missing=is_masked)
        metadata_vectors.append(vec)
        
    metadata_vectors = np.array(metadata_vectors)
    
    paths = df['full_path'].values
    ddx_labels = df['ddx_idx'].values
    eti_labels = df['etiology_family'].values
    
    ds = tf.data.Dataset.from_tensor_slices((paths, metadata_vectors, ddx_labels, eti_labels))
    
    if is_training:
        ds = ds.shuffle(buffer_size=10000, seed=42)
        
    AUTOTUNE = tf.data.AUTOTUNE
    
    ds = ds.map(
        lambda p, m, d, e: load_and_preprocess_multimodal(p, m, d, e, img_size=img_size), 
        num_parallel_calls=AUTOTUNE
    )
    
    ds = ds.batch(batch_size).prefetch(buffer_size=AUTOTUNE)
    return ds
