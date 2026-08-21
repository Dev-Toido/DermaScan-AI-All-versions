import pandas as pd
import numpy as np
import tensorflow as tf
import cv2
import os
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from tqdm import tqdm

print("Loading model...")
model = tf.keras.models.load_model("dermascan_v3_best.keras")

df = pd.read_csv("../data/processed/test.csv")

# V2 setup
AGE_MEAN = 54.58772832518652
AGE_STD = 18.188632571786233
v2_site_columns = [
    'site_anterior torso',
    'site_head/neck',
    'site_lateral torso',
    'site_lower extremity',
    'site_oral/genital',
    'site_palms/soles',
    'site_posterior torso',
    'site_upper extremity'
]

v2_to_isic = {0: 'NV', 1: 'MEL', 2: 'BKL', 3: 'DF', 4: 'SCC', 5: 'BCC', 6: 'VASC', 7: 'AK'}
ISIC_CLASSES = ["MEL", "NV", "BCC", "AK", "BKL", "DF", "VASC", "SCC"]

y_true = []
y_pred = []

print("Starting evaluation...")
for idx, row in tqdm(df.iterrows(), total=len(df)):
    img_name = row['image']
    img_path = f"../data/ISIC_2019_Training_Input/{img_name}.jpg"
    
    if not os.path.exists(img_path):
        continue
        
    # Read image
    img_cv2 = cv2.imread(img_path)
    if img_cv2 is None:
        continue
    img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
    
    # Preprocess Image
    img_resized = cv2.resize(img_cv2, (224, 224))
    img_normalized = img_resized.astype(np.float32)  # NO DIV BY 255.0
    img_input = np.expand_dims(img_normalized, axis=0)
    
    # Preprocess Metadata
    age = row['age_approx']
    if pd.isna(age):
        age = AGE_MEAN
    age_scaled = (age - AGE_MEAN) / AGE_STD
    
    sex = str(row['sex']).lower()
    if sex == 'female':
        sex_encoded = 1.0
    elif sex == 'male':
        sex_encoded = 0.0
    else:
        sex_encoded = 1.0  # unknown fallback to female (1.0)
        
    site = str(row['anatom_site_general']).lower()
    site_key = f"site_{site}"
    site_encoded = np.zeros(len(v2_site_columns), dtype=np.float32)
    if site_key in v2_site_columns:
        s_idx = v2_site_columns.index(site_key)
        site_encoded[s_idx] = 1.0
        
    meta_features = np.concatenate([
        [age_scaled],
        [sex_encoded],
        site_encoded
    ]).astype(np.float32).reshape(1, -1)
    
    # Predict
    preds = model.predict([img_input, meta_features], verbose=0)
    pred_idx_v2 = np.argmax(preds[0])
    
    # Map to ISIC string
    pred_isic_str = v2_to_isic[pred_idx_v2]
    
    # Add to lists
    y_pred.append(pred_isic_str)
    
    # True label
    true_isic_str = row['label_str']
    y_true.append(true_isic_str)

# Calculate metrics
acc = accuracy_score(y_true, y_pred)
report = classification_report(y_true, y_pred, labels=ISIC_CLASSES)
cm = confusion_matrix(y_true, y_pred, labels=ISIC_CLASSES)

output_str = f"Final Evaluation Report\n"
output_str += f"=======================\n"
output_str += f"Accuracy: {acc:.4f}\n\n"
output_str += f"Classification Report:\n{report}\n\n"
output_str += f"Confusion Matrix:\n{cm}\n"

print(output_str)

with open("evaluation_report.txt", "w") as f:
    f.write(output_str)
