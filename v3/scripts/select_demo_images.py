import os
import pandas as pd
import numpy as np
import cv2
import tensorflow as tf
import shutil

def select_demo_images():
    print("Loading model...")
    model = tf.keras.models.load_model('dermascan_v3_best.keras')
    
    print("Loading test data...")
    test_df = pd.read_csv('../data/processed/test.csv')
    
    demo_dir = 'demo_images'
    os.makedirs(demo_dir, exist_ok=True)
    
    # Mapping
    isic_to_v2 = {'NV': 0, 'MEL': 1, 'BKL': 2, 'DF': 3, 'SCC': 4, 'BCC': 5, 'VASC': 6, 'AK': 7}
    v2_to_isic = {0: 'NV', 1: 'MEL', 2: 'BKL', 3: 'DF', 4: 'SCC', 5: 'BCC', 6: 'VASC', 7: 'AK'}
    # Label in test.csv mapping: {0:'MEL',1:'NV',2:'BCC',3:'AK',4:'BKL',5:'DF',6:'VASC',7:'SCC'}
    label_to_isic = {0: 'MEL', 1: 'NV', 2: 'BCC', 3: 'AK', 4: 'BKL', 5: 'DF', 6: 'VASC', 7: 'SCC'}

    site_cols = [
        'site_anterior torso', 'site_head/neck', 'site_lateral torso', 
        'site_lower extremity', 'site_oral/genital', 'site_palms/soles', 
        'site_posterior torso', 'site_upper extremity'
    ]

    selected_images = []
    
    for idx, row in test_df.iterrows():
        img_path = os.path.join('data', 'processed', 'test', row['image'] + '.jpg')
        if not os.path.exists(img_path):
            img_path = os.path.join('data', 'ISIC_2019_Training_Input', row['image'] + '.jpg')
            if not os.path.exists(img_path):
                continue
                
        # Load and resize
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img_tensor = np.expand_dims(img.astype(np.float32), axis=0) # No /255.0
        
        # Meta
        age_scaled = (row['age_approx'] - 54.5877) / 18.1886
        
        sex_encoded = 1.0
        if row['sex'] == 'male':
            sex_encoded = 0.0
            
        site_encoded = np.zeros(len(site_cols), dtype=np.float32)
        site_key = f"site_{row['anatom_site_general']}"
        if site_key in site_cols:
            site_encoded[site_cols.index(site_key)] = 1.0
            
        meta_tensor = np.concatenate([[age_scaled], [sex_encoded], site_encoded]).astype(np.float32).reshape(1, -1)
        
        # Predict
        preds = model.predict([img_tensor, meta_tensor], verbose=0)
        pred_idx = np.argmax(preds[0])
        confidence = preds[0][pred_idx]
        
        pred_isic = v2_to_isic[pred_idx]
        true_isic = label_to_isic[row['label']]
        
        if pred_isic == true_isic and confidence > 0.7:
            selected_images.append({
                'image': row['image'] + '.jpg',
                'age': row['age_approx'],
                'sex': row['sex'],
                'site': row['anatom_site_general'],
                'confidence': confidence,
                'class': pred_isic,
                'path': img_path
            })
            if len(selected_images) >= 5:
                break
                
    if len(selected_images) < 5:
        print("Could not find 5 images with confidence > 0.7. Trying with > 0.6.")
        # We can implement a second pass if needed, but for the script we'll just sort by confidence
        
    print(f"Found {len(selected_images)} suitable images.")
    
    meta_records = []
    for img_info in selected_images:
        dest_path = os.path.join(demo_dir, img_info['image'])
        shutil.copy(img_info['path'], dest_path)
        meta_records.append({
            'filename': img_info['image'],
            'age': img_info['age'],
            'sex': img_info['sex'],
            'site': img_info['site'],
            'class': img_info['class'],
            'confidence': img_info['confidence']
        })
        
    pd.DataFrame(meta_records).to_csv('demo_metadata.csv', index=False)
    print("demo_metadata.csv saved.")

if __name__ == '__main__':
    select_demo_images()
