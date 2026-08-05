import os
import cv2
import numpy as np
import tensorflow as tf
from gradcam import generate_gradcam, overlay_heatmap
import pickle
import pandas as pd
from PIL import Image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
print("Loading model...")
model = tf.keras.models.load_model('dermascan_v3_best.keras')

df = pd.read_csv('demo_metadata.csv')
out_dir = 'website/assets'
os.makedirs(out_dir, exist_ok=True)

IMAGE_SIZE = (224, 224)

print("Generating demo images...")
for _, row in df.iterrows():
    filename = row['filename']
    img_id = filename.split('.')[0]
    img_path = os.path.join('demo_images', filename)
    
    if not os.path.exists(img_path):
        continue
        
    image_pil = Image.open(img_path).convert("RGB")
    img_cv2 = np.array(image_pil)
    
    img_resized = cv2.resize(img_cv2, IMAGE_SIZE)
    img_normalized = img_resized.astype(np.float32)
    
    age = row['age']
    sex = row['sex']
    site = row['site']
    
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

    AGE_MEAN = 54.58772832518652
    AGE_STD = 18.188632571786233
    age_scaled = (age - AGE_MEAN) / AGE_STD

    if sex.lower() == 'female':
        sex_encoded = 1.0
    else:
        sex_encoded = 0.0

    site_encoded = np.zeros(len(v2_site_columns), dtype=np.float32)
    site_key = f"site_{site.lower()}"
    if site_key in v2_site_columns:
        idx = v2_site_columns.index(site_key)
        site_encoded[idx] = 1.0

    meta_features = np.concatenate([
        [age_scaled],
        [sex_encoded],
        site_encoded
    ]).astype(np.float32).reshape(1, -1)
    
    img_input = np.expand_dims(img_normalized, axis=0)
    preds = model.predict([img_input, meta_features], verbose=0)
    pred_idx = np.argmax(preds[0])
    
    heatmap = generate_gradcam(model, img_normalized, pred_idx, meta_features)
    
    # Original
    original_uint8 = np.uint8(img_normalized)
    original_bgr = cv2.cvtColor(original_uint8, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(out_dir, f'demo_{img_id}_original.jpg'), original_bgr)
    
    # Heatmap
    heatmap_colored = np.uint8(255 * heatmap)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    cv2.imwrite(os.path.join(out_dir, f'demo_{img_id}_heatmap.jpg'), heatmap_colored)
    
    # Overlay
    superimposed = overlay_heatmap(img_normalized / 255.0, heatmap)
    # The overlay_heatmap function takes image in range [0, 1] and returns a uint8 BGR-like object actually? Wait.
    # From gradcam.py:
    # superimposed = cv2.addWeighted(img_uint8, 1 - alpha, heatmap_colored, alpha, 0)
    # So superimposed is uint8 RGB or BGR depending on what img_uint8 was.
    # img_uint8 was generated from img_normalized/255.0. It is RGB.
    # So we need to convert superimposed to BGR.
    superimposed_bgr = cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(out_dir, f'demo_{img_id}_gradcam.jpg'), superimposed_bgr)
    
print("Assets generated successfully!")
