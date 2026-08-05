import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
import os
import sys
import traceback

sys.path.append(".")
from clinical_mapper import map_prediction
from gradcam import generate_gradcam, overlay_heatmap
from safety_net import check_skin_lesion

def run_bulk_test(num_images=500):
    print("Loading model...")
    model = tf.keras.models.load_model("dermascan_v3_best.keras")
    
    print(f"Loading top {num_images} from test.csv...")
    df = pd.read_csv("../data/processed/test.csv").head(num_images)
    
    # Tracking metrics
    metrics = {
        "total_attempted": len(df),
        "not_found": 0,
        "failed_safety_net": 0,
        "successful_predictions": 0,
        "low_confidence_flagged": 0,
        "gradcam_success": 0,
        "gradcam_failures": 0,
        "errors": 0
    }
    
    AGE_MEAN = 54.58772832518652
    AGE_STD = 18.188632571786233
    v2_site_columns = [
        'site_anterior torso', 'site_head/neck', 'site_lateral torso',
        'site_lower extremity', 'site_oral/genital', 'site_palms/soles',
        'site_posterior torso', 'site_upper extremity'
    ]
    v2_to_isic = {0: 'NV', 1: 'MEL', 2: 'BKL', 3: 'DF', 4: 'SCC', 5: 'BCC', 6: 'VASC', 7: 'AK'}

    print("Starting bulk test pipeline...")
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"Processing image {idx}/{num_images}...")
            
        try:
            img_name = row['image']
            img_path = f"../data/ISIC_2019_Training_Input/{img_name}.jpg"
            
            if not os.path.exists(img_path):
                metrics["not_found"] += 1
                continue
                
            image_pil = Image.open(img_path).convert("RGB")
            img_cv2 = np.array(image_pil)
            
            # 1. Safety Net
            if not check_skin_lesion(img_cv2):
                metrics["failed_safety_net"] += 1
                # In the app it just shows a warning, we will continue but log it.
            
            # 2. Preprocess
            img_resized = cv2.resize(img_cv2, (224, 224))
            img_normalized = img_resized.astype(np.float32)
            
            age = row['age_approx']
            if pd.isna(age): age = AGE_MEAN
            age_scaled = (age - AGE_MEAN) / AGE_STD
            
            sex = str(row['sex']).lower()
            if sex == 'female': sex_encoded = 1.0
            elif sex == 'male': sex_encoded = 0.0
            else: sex_encoded = 1.0
                
            site = str(row['anatom_site_general']).lower()
            site_encoded = np.zeros(len(v2_site_columns), dtype=np.float32)
            site_key = f"site_{site}"
            if site_key in v2_site_columns:
                s_idx = v2_site_columns.index(site_key)
                site_encoded[s_idx] = 1.0
                
            meta_features = np.concatenate([
                [age_scaled], [sex_encoded], site_encoded
            ]).astype(np.float32).reshape(1, -1)
            
            img_input = np.expand_dims(img_normalized, axis=0)
            
            # 3. Model Prediction
            preds = model.predict([img_input, meta_features], verbose=0)
            pred_idx = np.argmax(preds[0])
            confidence = float(preds[0][pred_idx])
            metrics["successful_predictions"] += 1
            
            # 4. Clinical Mapper
            isic_abbr = v2_to_isic[pred_idx]
            mapping = map_prediction(isic_abbr, confidence)
            if confidence < 0.6:
                metrics["low_confidence_flagged"] += 1
                
            # 5. Grad-CAM
            try:
                heatmap = generate_gradcam(model, img_normalized, pred_idx)
                overlay = overlay_heatmap(img_normalized / 255.0, heatmap)
                if overlay is not None:
                    metrics["gradcam_success"] += 1
            except Exception as e:
                metrics["gradcam_failures"] += 1
                
        except Exception as e:
            metrics["errors"] += 1
            traceback.print_exc()

    print("\n--- BULK TEST REPORT ---")
    for k, v in metrics.items():
        print(f"{k}: {v}")
        
    with open("bulk_test_results.txt", "w") as f:
        f.write("# App V3 Pipeline End-to-End Test Results (500 images)\n\n")
        for k, v in metrics.items():
            f.write(f"- **{k}**: {v}\n")

if __name__ == "__main__":
    run_bulk_test(500)
