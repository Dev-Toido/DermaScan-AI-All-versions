import pandas as pd
import numpy as np
import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)

# Load test set
df = pd.read_csv('data/processed/test.csv')

# Fixed random seed
np.random.seed(42)

sampled_dfs = []
for label in range(8):
    class_df = df[df['label'] == label]
    if len(class_df) < 50:
        logging.warning(f"Class {label} has only {len(class_df)} samples in test set. Sampling with replacement.")
        sampled_dfs.append(class_df.sample(n=50, replace=True, random_state=42))
    else:
        sampled_dfs.append(class_df.sample(n=50, random_state=42))

balanced_df = pd.concat(sampled_dfs).reset_index(drop=True)

# Ensure portability by only keeping a few columns
cols_to_keep = ['image', 'label', 'age_approx', 'sex', 'anatom_site_general']
# But wait, we need the site_ columns for the evaluation later?
# The user specified:
# "Include at least these columns: image, label, age_approx, sex, anatom_site_general. Also include the V3 label mapping for reference..."
# The user also says: "Metadata: Build a 10-element vector exactly as: age_scaled, sex_encoded, One-hot site encoding for the 8 specific V2 columns..."
# The `site_*` columns must be present in the CSV if the evaluation script reads it, or the evaluation script must compute them from `anatom_site_general`.
# Let's keep all original columns just in case, but definitely the ones requested.
cols_to_keep = list(balanced_df.columns) # keeping all to be safe

os.makedirs('balanced_test/images', exist_ok=True)

missing_images = 0
for idx, row in balanced_df.iterrows():
    img_name = row['image']
    # Check possible extensions
    src_path = f"data/ISIC_2019_Training_Input/{img_name}.jpg"
    if not os.path.exists(src_path):
        src_path = f"data/ISIC_2019_Training_Input/{img_name}_downsampled.jpg"
        
    dst_path = f"balanced_test/images/{img_name}.jpg"
    
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
    else:
        logging.warning(f"Image not found: {img_name}")
        missing_images += 1

balanced_df.to_csv('balanced_test/balanced_test.csv', index=False)

with open('balanced_test/label_mapping.txt', 'w') as f:
    f.write("0:MEL, 1:NV, 2:BCC, 3:AK, 4:BKL, 5:DF, 6:VASC, 7:SCC\n")

print(f"Created balanced_test with {len(balanced_df)} images (50 per class). Missing images: {missing_images}")
