import pandas as pd
import os
from sklearn.model_selection import train_test_split
import shutil

def standardize_and_merge(isic_csv_path, diverse_csv_path, output_dir):
    """
    Simulated Agent Workflow: Schema Analysis & Standardization.
    Standardizes ISIC and Diverse (e.g., DDI) datasets to have similar fields,
    mixes them, and segregates them into 70/15/15 parts.
    """
    print("Agent 1 [Schema Analyzer]: Reading datasets...")
    
    # 1. Load Data (assuming generic CSV format for now)
    try:
        isic_df = pd.read_csv(isic_csv_path)
        diverse_df = pd.read_csv(diverse_csv_path)
    except FileNotFoundError:
        print("Data files not found. Awaiting dataset download.")
        return
        
    print("Agent 2 [Standardizer]: Aligning metadata fields...")
    # 2. Standardize Fields
    # ISIC typical fields: image, age_approx, anatom_site_general_challenge, sex, diagnosis
    # We rename them to a unified format.
    isic_standard = pd.DataFrame({
        'image_id': isic_df['image'],
        'age': isic_df['age_approx'],
        'sex': isic_df['sex'],
        'site': isic_df['anatom_site_general_challenge'],
        'diagnosis': isic_df['diagnosis'],
        'source': 'ISIC'
    })
    
    # DDI typical fields: DDI_ID, age, gender, skin_tone, malignant, disease
    diverse_standard = pd.DataFrame({
        'image_id': diverse_df['DDI_ID'] if 'DDI_ID' in diverse_df else diverse_df.iloc[:, 0],
        'age': diverse_df['age'] if 'age' in diverse_df else None,
        'sex': diverse_df['gender'] if 'gender' in diverse_df else None,
        'site': 'unknown', # Handle missing with Modality Dropout
        'diagnosis': diverse_df['disease'] if 'disease' in diverse_df else 'unknown',
        'source': 'Diverse'
    })
    
    # 3. Mixing / Merging
    print("Agent 3 [Data Mixer]: Mixing datasets into unified pool...")
    unified_df = pd.concat([isic_standard, diverse_standard], ignore_index=True)
    
    # Shuffle the dataset thoroughly
    unified_df = unified_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 4. Segregation into 70 / 15 / 15 parts
    print("Agent 4 [Segregator]: Splitting into 70% Train, 15% Val, 15% Test...")
    
    # Split 1: 70% Train, 30% Temp (Val + Test)
    train_df, temp_df = train_test_split(unified_df, test_size=0.30, random_state=42, stratify=unified_df['diagnosis'])
    
    # Split 2: Divide the 30% Temp into 15% Val and 15% Test (which is 50% of the Temp)
    val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=42, stratify=temp_df['diagnosis'])
    
    print(f"Split Complete:")
    print(f" - Train: {len(train_df)} ({len(train_df)/len(unified_df):.0%})")
    print(f" - Val:   {len(val_df)} ({len(val_df)/len(unified_df):.0%})")
    print(f" - Test:  {len(test_df)} ({len(test_df)/len(unified_df):.0%})")
    
    # 5. Save the splits
    os.makedirs(output_dir, exist_ok=True)
    train_df.to_csv(os.path.join(output_dir, 'train_metadata.csv'), index=False)
    val_df.to_csv(os.path.join(output_dir, 'val_metadata.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, 'test_metadata.csv'), index=False)
    
    print("Agent Workflow Complete! Data is ready for Label Mapping.")

if __name__ == "__main__":
    standardize_and_merge("../../archive/ISIC_2019.csv", "../../archive/Diverse.csv", "../train/")
