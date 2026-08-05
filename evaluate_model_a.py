import os
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, accuracy_score

# Paths
MODEL_PATH = 'dermascan_v3_best.keras'
CSV_PATH = 'balanced_test/balanced_test.csv'
IMG_DIR = 'balanced_test/images'
OUT_PATH = 'balanced_test/model_a_results.txt'

df = pd.read_csv(CSV_PATH)

# Output mappings
V2_MAP = {0:'NV', 1:'MEL', 2:'BKL', 3:'DF', 4:'SCC', 5:'BCC', 6:'VASC', 7:'AK'}
V3_MAP = {'MEL':0, 'NV':1, 'BCC':2, 'AK':3, 'BKL':4, 'DF':5, 'VASC':6, 'SCC':7}

# Preprocess metadata
def preprocess_metadata(row):
    # age
    age = row['age_approx']
    if pd.isna(age):
        age = 54.58772832518652
    age_scaled = (age - 54.58772832518652) / 18.188632571786233
    
    # sex
    sex = row['sex']
    if sex == 'male':
        sex_encoded = 0.0
    else:
        sex_encoded = 1.0 # fallback female or unknown
        
    # site
    site = row['anatom_site_general']
    sites = [
        'anterior torso', 'head/neck', 'lateral torso', 'lower extremity',
        'oral/genital', 'palms/soles', 'posterior torso', 'upper extremity'
    ]
    site_vec = [1.0 if site == s else 0.0 for s in sites]
    
    return np.array([age_scaled, sex_encoded] + site_vec, dtype=np.float32)

meta_inputs = np.array([preprocess_metadata(row) for _, row in df.iterrows()])

# Preprocess image
def load_img(img_name):
    path = os.path.join(IMG_DIR, f"{img_name}.jpg")
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, [224, 224])
    return img

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# Warmup
print("Warming up...")
dummy_imgs = np.zeros((5, 224, 224, 3), dtype=np.float32)
dummy_meta = np.zeros((5, 10), dtype=np.float32)
model.predict([dummy_imgs, dummy_meta], verbose=0)

y_true = []
y_pred = []
inference_times = []

print("Running inference...")
for i, row in df.iterrows():
    img = load_img(row['image'])
    img = tf.expand_dims(img, 0)
    meta = np.expand_dims(meta_inputs[i], 0)
    
    start_time = time.time()
    preds = model.predict([img, meta], verbose=0)
    inf_time = time.time() - start_time
    inference_times.append(inf_time)
    
    v2_idx = np.argmax(preds[0])
    isic_abbr = V2_MAP[v2_idx]
    v3_idx = V3_MAP[isic_abbr]
    
    y_true.append(row['label']) # This label matches V3 index
    y_pred.append(v3_idx)
    
    if (i+1) % 50 == 0:
        print(f"Processed {i+1}/{len(df)} images...")

avg_time = np.mean(inference_times)
acc = accuracy_score(y_true, y_pred)
target_names = ['MEL', 'NV', 'BCC', 'AK', 'BKL', 'DF', 'VASC', 'SCC']
report = classification_report(y_true, y_pred, target_names=target_names)

# Sensitivity for malignant classes (MEL, BCC, SCC) -> indices 0, 2, 7
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_true, y_pred)
# sensitivity = TP / (TP + FN) = cm[i,i] / sum(cm[i,:])
sens_mel = cm[0,0] / np.sum(cm[0,:])
sens_bcc = cm[2,2] / np.sum(cm[2,:])
sens_scc = cm[7,7] / np.sum(cm[7,:])

output = f"Accuracy: {acc:.4f}\n"
output += f"Average Inference Time: {avg_time:.4f} seconds/image\n\n"
output += "Sensitivity for Malignant Classes:\n"
output += f"- MEL (Melanoma): {sens_mel:.4f}\n"
output += f"- BCC (Basal Cell Carcinoma): {sens_bcc:.4f}\n"
output += f"- SCC (Squamous Cell Carcinoma): {sens_scc:.4f}\n\n"
output += "Classification Report:\n"
output += report

with open(OUT_PATH, 'w') as f:
    f.write(output)

print(f"Evaluation complete. Results saved to {OUT_PATH}")
