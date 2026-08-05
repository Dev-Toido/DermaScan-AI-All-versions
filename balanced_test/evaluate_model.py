import argparse
import os
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

def main():
    parser = argparse.ArgumentParser(description="Evaluate a Keras model on the balanced test set.")
    parser.add_argument('model_path', type=str, help="Path to the .h5 or .keras model file")
    parser.add_argument('--normalize', action='store_true', help="Flag: if set, normalize image pixels to [0, 1]. Otherwise keep [0, 255].")
    args = parser.parse_args()
    
    # ---------------------------------------------------------
    # USER CONFIGURATION AREA
    # ---------------------------------------------------------
    # Update this mapping to match the order of outputs from your model.
    # The default assumes your model outputs the 8 ISIC classes in standard order:
    # 0: MEL, 1: NV, 2: BCC, 3: AK, 4: BKL, 5: DF, 6: VASC, 7: SCC
    MODEL_OUTPUT_ORDER = {
        0: 'MEL', 1: 'NV', 2: 'BCC', 3: 'AK', 4: 'BKL', 5: 'DF', 6: 'VASC', 7: 'SCC'
    }
    
    # Do not change this map - this is the standard evaluation order.
    STANDARD_MAP = {'MEL':0, 'NV':1, 'BCC':2, 'AK':3, 'BKL':4, 'DF':5, 'VASC':6, 'SCC':7}
    
    # ---------------------------------------------------------
    
    CSV_PATH = 'balanced_test.csv'
    IMG_DIR = 'images'
    OUT_PATH = 'model_b_results.txt'
    
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    print(f"Loading model from {args.model_path}...")
    model = tf.keras.models.load_model(args.model_path, compile=False)
    
    # Try to determine input shape for images
    try:
        input_shape = model.inputs[0].shape[1:3]
        if input_shape[0] is None:
            img_size = (224, 224)
        else:
            img_size = tuple(input_shape)
    except:
        img_size = (224, 224)
    print(f"Using image size: {img_size}")
    
    # Check if model is multimodal (takes metadata)
    is_multimodal = len(model.inputs) > 1
    
    def load_img(img_name):
        path = os.path.join(IMG_DIR, f"{img_name}.jpg")
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, img_size)
        if args.normalize:
            img = img / 255.0
        return img
        
    def preprocess_metadata(row):
        # NOTE: If your model requires a specific metadata vector, adjust this!
        # This provides the 10-element vector used by Model A.
        age = row['age_approx']
        if pd.isna(age):
            age = 54.58772832518652
        age_scaled = (age - 54.58772832518652) / 18.188632571786233
        
        sex = row['sex']
        sex_encoded = 0.0 if sex == 'male' else 1.0
            
        site = row['anatom_site_general']
        sites = [
            'anterior torso', 'head/neck', 'lateral torso', 'lower extremity',
            'oral/genital', 'palms/soles', 'posterior torso', 'upper extremity'
        ]
        site_vec = [1.0 if site == s else 0.0 for s in sites]
        
        return np.array([age_scaled, sex_encoded] + site_vec, dtype=np.float32)

    meta_inputs = np.array([preprocess_metadata(row) for _, row in df.iterrows()])
    
    # Warmup
    print("Warming up...")
    dummy_imgs = np.zeros((5, *img_size, 3), dtype=np.float32)
    dummy_meta = np.zeros((5, 10), dtype=np.float32)
    if is_multimodal:
        model.predict([dummy_imgs, dummy_meta], verbose=0)
    else:
        model.predict(dummy_imgs, verbose=0)
        
    y_true = []
    y_pred = []
    inference_times = []
    
    print("Running inference...")
    for i, row in df.iterrows():
        img = load_img(row['image'])
        img = tf.expand_dims(img, 0)
        
        start_time = time.time()
        if is_multimodal:
            meta = np.expand_dims(meta_inputs[i], 0)
            preds = model.predict([img, meta], verbose=0)
        else:
            preds = model.predict(img, verbose=0)
            
        inf_time = time.time() - start_time
        inference_times.append(inf_time)
        
        # Mapping predicted index to standard index
        pred_idx = np.argmax(preds[0])
        if pred_idx not in MODEL_OUTPUT_ORDER:
            raise ValueError(f"Model predicted index {pred_idx}, which is not in MODEL_OUTPUT_ORDER.")
        isic_abbr = MODEL_OUTPUT_ORDER[pred_idx]
        standard_idx = STANDARD_MAP[isic_abbr]
        
        y_true.append(row['label'])
        y_pred.append(standard_idx)
        
        if (i+1) % 50 == 0:
            print(f"Processed {i+1}/{len(df)} images...")

    avg_time = np.mean(inference_times)
    acc = accuracy_score(y_true, y_pred)
    target_names = ['MEL', 'NV', 'BCC', 'AK', 'BKL', 'DF', 'VASC', 'SCC']
    report = classification_report(y_true, y_pred, target_names=target_names)
    
    cm = confusion_matrix(y_true, y_pred)
    sens_mel = cm[0,0] / np.sum(cm[0,:]) if np.sum(cm[0,:]) > 0 else 0
    sens_bcc = cm[2,2] / np.sum(cm[2,:]) if np.sum(cm[2,:]) > 0 else 0
    sens_scc = cm[7,7] / np.sum(cm[7,:]) if np.sum(cm[7,:]) > 0 else 0
    
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

if __name__ == "__main__":
    main()
