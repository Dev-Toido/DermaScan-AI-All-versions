import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report
import os, pickle

IMG_SIZE = (224, 224)
BATCH = 32
DATA_DIR = 'data/ISIC_2019_Training_Input'

# Load model
model = tf.keras.models.load_model('dermascan_v3_best.keras')

# Load test split
test_df = pd.read_csv('data/processed/test.csv')
file_paths = test_df['image'].apply(lambda x: os.path.join(DATA_DIR, f'{x}.jpg')).values

# True labels in V3 order (ISIC original): MEL=0, NV=1, BCC=2, AK=3, BKL=4, DF=5, VASC=6, SCC=7
y_true_v3 = test_df['label'].values

# V2 model's class order (from training data)
v2_order = ['Melanocytic Nevi', 'Melanoma', 'Benign Keratosis', 'Dermatofibroma',
            'Squamous Cell Carcinoma', 'Basal Cell Carcinoma', 'Vascular Lesion',
            'Actinic Keratosis']

# V3 (ISIC) class abbreviations in order of label 0-7
v3_abbrev = ['MEL', 'NV', 'BCC', 'AK', 'BKL', 'DF', 'VASC', 'SCC']

# Manual mapping: V3 index -> V2 index
# V3: MEL(0) -> V2 'Melanoma' (index 1)
# V3: NV(1) -> V2 'Melanocytic Nevi' (index 0)
# V3: BCC(2) -> V2 'Basal Cell Carcinoma' (index 5)
# V3: AK(3) -> V2 'Actinic Keratosis' (index 7)
# V3: BKL(4) -> V2 'Benign Keratosis' (index 2)
# V3: DF(5) -> V2 'Dermatofibroma' (index 3)
# V3: VASC(6) -> V2 'Vascular Lesion' (index 6)
# V3: SCC(7) -> V2 'Squamous Cell Carcinoma' (index 4)
v3_to_v2_idx = {0:1, 1:0, 2:5, 3:7, 4:2, 5:3, 6:6, 7:4}

# Build metadata (same V2 format as before, 10 features)
AGE_MEAN = 54.58772832518652
AGE_STD = 18.188632571786233
test_df['age_raw'] = test_df['age_approx'].fillna(test_df['age_approx'].median())
test_df['age_scaled'] = (test_df['age_raw'] - AGE_MEAN) / AGE_STD

test_df['sex_encoded'] = test_df['sex'].map({'male':1.0, 'female':0.0}).fillna(0.0)

v2_site_cols = ['site_anterior torso', 'site_head/neck', 'site_lateral torso',
                'site_lower extremity', 'site_oral/genital', 'site_palms/soles',
                'site_posterior torso', 'site_upper extremity']
site_matrix = np.zeros((len(test_df), 8), dtype=np.float32)
for i, site in enumerate(test_df['anatom_site_general']):
    if site in v2_site_cols:
        idx = v2_site_cols.index(site)
        site_matrix[i, idx] = 1.0

meta = np.column_stack([test_df['age_scaled'].values,
                        test_df['sex_encoded'].values,
                        site_matrix]).astype(np.float32)

# Dataset
def load_fn(path, meta, label):
    img = tf.io.read_file(path)
    img = tf.io.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    return (img, meta), label

ds = tf.data.Dataset.from_tensor_slices((file_paths, meta, y_true_v3))
ds = ds.map(load_fn, num_parallel_calls=tf.data.AUTOTUNE).batch(BATCH).prefetch(tf.data.AUTOTUNE)

# Predict (outputs probabilities in V2 order)
y_pred_prob = model.predict(ds)
y_pred_v2 = np.argmax(y_pred_prob, axis=1)  # index in V2 order

# Convert V2 predictions to V3 index using reverse mapping
v2_to_v3_idx = {v: k for k, v in v3_to_v2_idx.items()}
y_pred_v3 = np.array([v2_to_v3_idx.get(p, -1) for p in y_pred_v2])

# Accuracy
acc = accuracy_score(y_true_v3, y_pred_v3)
print(f'Overall Accuracy (corrected): {acc:.4f} ({acc*100:.2f}%)')

# Report with V3 class names
print(classification_report(y_true_v3, y_pred_v3, target_names=v3_abbrev, zero_division=0))