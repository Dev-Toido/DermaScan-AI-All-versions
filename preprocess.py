"""
preprocess.py
Data preprocessing pipeline for DermaScan AI V3 (ISIC 2019 dataset).
Corrected: data splitting BEFORE fitting encoders/scalers, 380x380 images.
"""

import pandas as pd
import numpy as np
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import pickle
import logging
import argparse
from typing import Tuple, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

IMAGE_SIZE = (380, 380)   # EfficientNetB4 native resolution


def load_and_merge(data_dir: str) -> pd.DataFrame:
    """Load metadata and ground truth, merge, extract label, drop missing images."""
    metadata_path = os.path.join(data_dir, "ISIC_2019_Training_Metadata.csv")
    gt_path = os.path.join(data_dir, "ISIC_2019_Training_GroundTruth.csv")
    image_dir = os.path.join(data_dir, "ISIC_2019_Training_Input")
    
    metadata = pd.read_csv(metadata_path)
    gt = pd.read_csv(gt_path)
    
    df = pd.merge(metadata, gt, on="image")
    
    # Keep only rows whose image files actually exist
    file_exists = df['image'].apply(lambda x: os.path.isfile(os.path.join(image_dir, f"{x}.jpg")))
    removed = len(df) - file_exists.sum()
    if removed > 0:
        logging.warning(f"Removing {removed} rows with missing image files.")
    df = df[file_exists].reset_index(drop=True)
    
    label_cols = [col for col in gt.columns if col != 'image']
    df['label_str'] = df[label_cols].idxmax(axis=1)
    label_to_id = {col: i for i, col in enumerate(label_cols)}
    df['label'] = df['label_str'].map(label_to_id)
    return df, label_to_id, label_cols

def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stratified 70/15/15 split."""
    train, temp = train_test_split(df, test_size=0.30, stratify=df['label'], random_state=42)
    val, test = train_test_split(temp, test_size=0.50, stratify=temp['label'], random_state=42)
    return train, val, test


def preprocess_split(split_df: pd.DataFrame,
                     age_scaler: MinMaxScaler = None,
                     site_encoder: OneHotEncoder = None,
                     fit: bool = True) -> Tuple[pd.DataFrame, MinMaxScaler, OneHotEncoder]:
    """
    Apply missing value handling, encoding, and scaling to a single split.
    If fit=True, fit the scalers/encoders on this split (training). Otherwise transform only.
    """
    df = split_df.copy()
    
    # 1. Missing values
    df['sex'] = df['sex'].fillna('unknown')
    df['anatom_site_general'] = df['anatom_site_general'].fillna('unknown')
    
    df['age_missing'] = df['age_approx'].isnull().astype(int)
    median_age = df['age_approx'].median()
    df['age_approx'] = df['age_approx'].fillna(median_age)
    
    # 2. Age scaling
    if fit:
        age_scaler = MinMaxScaler()
        df['age_approx_normalized'] = age_scaler.fit_transform(df[['age_approx']])
    else:
        df['age_approx_normalized'] = age_scaler.transform(df[['age_approx']])
    
    # 3. Sex encoding (female=0, male=1, unknown=0.5)
    def encode_sex(val):
        if val == 'female': return 0.0
        elif val == 'male': return 1.0
        else: return 0.5
    df['sex_encoded'] = df['sex'].apply(encode_sex)
    
    # 4. Anatomic site one-hot
    if fit:
        site_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        site_encoded = site_encoder.fit_transform(df[['anatom_site_general']])
    else:
        site_encoded = site_encoder.transform(df[['anatom_site_general']])
    
    site_cols = [f"site_{cat}" for cat in site_encoder.categories_[0]]
    df_site = pd.DataFrame(site_encoded, columns=site_cols, index=df.index)
    df = pd.concat([df, df_site], axis=1)
    
    # Keep only necessary columns
    meta_cols = ['age_approx_normalized', 'age_missing', 'sex_encoded'] + site_cols
    # Ensure columns exist (in case some site categories are missing in val/test)
    for col in meta_cols:
        if col not in df.columns:
            df[col] = 0.0
    return df, age_scaler, site_encoder


def create_tf_dataset(df: pd.DataFrame, image_dir: str, batch_size: int = 32, is_training: bool = True) -> tf.data.Dataset:
    """Build tf.data pipeline for a preprocessed DataFrame split."""
    # Identify metadata columns
    site_cols = [col for col in df.columns if col.startswith('site_')]
    meta_cols = ['age_approx_normalized', 'age_missing', 'sex_encoded'] + site_cols
    
    file_paths = df['image'].apply(lambda x: os.path.join(image_dir, f"{x}.jpg")).values
    labels = df['label'].values
    metadata_features = df[meta_cols].values.astype(np.float32)
    
    dataset = tf.data.Dataset.from_tensor_slices((file_paths, metadata_features, labels))
    
    def parse_fn(file_path, meta, label):
        img = tf.io.read_file(file_path)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMAGE_SIZE)
        img = img / 255.0
        return (img, meta), label
    
    if is_training:
        dataset = dataset.shuffle(buffer_size=10000)
    dataset = dataset.map(parse_fn, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data", help="Path to the data folder")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size for tf.data (used in validation check)")
    args = parser.parse_args()
    
    data_dir = args.data_dir
    image_dir = os.path.join(data_dir, "ISIC_2019_Training_Input")
    out_dir = os.path.join(data_dir, "processed")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load and merge
    logging.info("Loading and merging data...")
    df, label_to_id, label_names = load_and_merge(data_dir)
    logging.info(f"Merged dataset shape: {df.shape}")
    
    # 2. Split first
    logging.info("Performing stratified split (70/15/15)...")
    train_df, val_df, test_df = split_data(df)
    logging.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    # 3. Preprocess each split (fit only on train)
    logging.info("Preprocessing training split (fitting encoders)...")
    train_processed, age_scaler, site_encoder = preprocess_split(train_df, fit=True)
    
    logging.info("Preprocessing validation split (transform only)...")
    val_processed, _, _ = preprocess_split(val_df, age_scaler=age_scaler, site_encoder=site_encoder, fit=False)
    
    logging.info("Preprocessing test split (transform only)...")
    test_processed, _, _ = preprocess_split(test_df, age_scaler=age_scaler, site_encoder=site_encoder, fit=False)
    
    # 4. Save processed splits
    train_processed.to_csv(os.path.join(out_dir, "train.csv"), index=False)
    val_processed.to_csv(os.path.join(out_dir, "val.csv"), index=False)
    test_processed.to_csv(os.path.join(out_dir, "test.csv"), index=False)
    logging.info(f"Processed CSVs saved to {out_dir}")
    
    # 5. Save preprocessing objects
    objects_to_save = {
        'age_scaler': age_scaler,
        'site_encoder': site_encoder,
        'label_to_id': label_to_id,
        'label_names': label_names,
        'image_size': IMAGE_SIZE,
        'median_age': train_df['age_approx'].median()   # from raw training data
    }
    with open("preprocessing_objects.pkl", "wb") as f:
        pickle.dump(objects_to_save, f)
    logging.info("Preprocessing objects saved to preprocessing_objects.pkl")
    
    # 6. Quick validation of tf.data pipeline on training set
    logging.info("Validating tf.data pipeline on training split...")
    try:
        train_ds = create_tf_dataset(train_processed, image_dir, batch_size=args.batch_size, is_training=True)
        for (img, meta), label in train_ds.take(1):
            logging.info(f"Image batch shape: {img.shape}")
            logging.info(f"Metadata batch shape: {meta.shape}")
            logging.info(f"Label batch shape: {label.shape}")
        logging.info("Pipeline test successful.")
    except Exception as e:
        logging.error(f"Pipeline test failed: {e}")
        return
    
    logging.info("Preprocessing complete. Ready for training.")
    logging.info(f"Final dataset size: {len(df)} images")

if __name__ == "__main__":
    main()