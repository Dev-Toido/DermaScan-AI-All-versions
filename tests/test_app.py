import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import os
import sys

# Add current dir to path to import local modules
sys.path.append(".")
from clinical_mapper import map_prediction, CLASS_NAMES
from gradcam import generate_gradcam, overlay_heatmap

def test_app():
    print("Loading model...")
    model = tf.keras.models.load_model("dermascan_v3_best.keras")
    IMAGE_SIZE = (224, 224)
    
    # Simulate user inputs
    age = 50
    sex = "male"
    site = "anterior torso"
    
    # Find a sample image
    test_img = "data/ISIC_2019_Training_Input/ISIC_0014688_downsampled.jpg"
    if not os.path.exists(test_img):
        print("Test image not found.")
        return
        
    image_pil = Image.open(test_img).convert("RGB")
    img_cv2 = np.array(image_pil)
    
    artifact_dir = "/home/dev-toido/.gemini/antigravity-ide/brain/5ca0a3d8-ede0-4fd2-913a-798cc676cb81/scratch"
    os.makedirs(artifact_dir, exist_ok=True)
    image_pil.save(f"{artifact_dir}/original_input.jpg")
    
    print("Preprocessing...")
    # Preprocess Image
    img_resized = cv2.resize(img_cv2, IMAGE_SIZE)
    img_normalized = img_resized.astype(np.float32)
    
    # Preprocess Metadata
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

    if sex == 'female':
        sex_encoded = 1.0
    elif sex == 'male':
        sex_encoded = 0.0
    else:
        sex_encoded = 1.0

    site_encoded = np.zeros(len(v2_site_columns), dtype=np.float32)
    site_key = f"site_{site}"
    if site_key in v2_site_columns:
        idx = v2_site_columns.index(site_key)
        site_encoded[idx] = 1.0
    print("Site encoded:", site_encoded)
    
    # Let's see what happens next
    meta_features = np.concatenate([
        [age_scaled],
        [sex_encoded],
        site_encoded
    ]).astype(np.float32).reshape(1, -1)
    
    img_input = np.expand_dims(img_normalized, axis=0)
    
    print("Predicting...")
    preds = model.predict([img_input, meta_features])
    pred_idx = np.argmax(preds[0])
    confidence = float(preds[0][pred_idx])
    
    v2_to_isic = {0: 'NV', 1: 'MEL', 2: 'BKL', 3: 'DF', 4: 'SCC', 5: 'BCC', 6: 'VASC', 7: 'AK'}
    isic_abbr = v2_to_isic[pred_idx]
    
    print("Mapping prediction...")
    mapping = map_prediction(isic_abbr, confidence)
    print(f"Mapped: {mapping['class_full']} ({confidence:.2f})")
    
    print("Generating Grad-CAM...")
    try:
        heatmap = generate_gradcam(model, img_normalized, pred_idx)
        overlay = overlay_heatmap(img_normalized / 255.0, heatmap)
        print("Grad-CAM generated successfully, overlay shape:", overlay.shape)
        
        # Save overlay image
        Image.fromarray(overlay).save(f"{artifact_dir}/gradcam_overlay.jpg")
        print(f"Saved original and overlay images to {artifact_dir}")
    except Exception as e:
        print("Grad-CAM failed:", e)

if __name__ == "__main__":
    test_app()
