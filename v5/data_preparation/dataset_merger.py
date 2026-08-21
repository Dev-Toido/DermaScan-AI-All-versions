import pandas as pd
import os
from sklearn.model_selection import train_test_split

def standardize_and_merge(isic_meta_path, isic_gt_path, diverse_csv_path, output_dir):
    """
    Simulated Agent Workflow: Schema Analysis & Standardization.
    Standardizes ISIC and Diverse (DDI) datasets, mixes them, and segregates them 70/15/15.
    """
    print("Agent 1 [Schema Analyzer]: Reading datasets...")
    
    try:
        isic_meta = pd.read_csv(isic_meta_path)
        isic_gt = pd.read_csv(isic_gt_path)
        diverse_df = pd.read_csv(diverse_csv_path)
    except FileNotFoundError as e:
        print(f"Data files not found: {e}")
        return
        
    print("Agent 2 [Standardizer]: Aligning metadata fields...")
    
    # 1. Handle ISIC Ground Truth (One-hot to single column)
    diag_cols = [c for c in isic_gt.columns if c != 'image' and c != 'UNK']
    isic_gt['diagnosis'] = isic_gt[diag_cols].idxmax(axis=1)
    isic_df = pd.merge(isic_meta, isic_gt[['image', 'diagnosis']], on='image')
    
    # Standardize ISIC
    isic_standard = pd.DataFrame({
        'image_id': isic_df['image'],
        'age': isic_df['age_approx'],
        'sex': isic_df['sex'],
        'site': isic_df['anatom_site_general'],
        'diagnosis': isic_df['diagnosis'],
        'source': 'ISIC'
    })
    
    # Standardize DDI
    diverse_standard = pd.DataFrame({
        'image_id': diverse_df['DDI_ID'] if 'DDI_ID' in diverse_df else diverse_df.iloc[:, 0],
        'age': diverse_df['age'] if 'age' in diverse_df else None,
        'sex': diverse_df['gender'] if 'gender' in diverse_df else None,
        'site': 'unknown',
        'diagnosis': diverse_df['disease'] if 'disease' in diverse_df else 'unknown',
        'source': 'Diverse'
    })
    
    print("Agent 3 [Data Mixer]: Mixing datasets into unified pool...")
    unified_df = pd.concat([isic_standard, diverse_standard], ignore_index=True)
    unified_df = unified_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("Agent 4 [Segregator]: Splitting into 70% Train, 15% Val, 15% Test...")
    train_df, temp_df = train_test_split(unified_df, test_size=0.30, random_state=42, stratify=unified_df['source'])
    val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=42, stratify=temp_df['source'])
    
    print(f"Split Complete:")
    print(f" - Train: {len(train_df)} ({len(train_df)/len(unified_df):.0%})")
    print(f" - Val:   {len(val_df)} ({len(val_df)/len(unified_df):.0%})")
    print(f" - Test:  {len(test_df)} ({len(test_df)/len(unified_df):.0%})")
    
    os.makedirs(output_dir, exist_ok=True)
    train_df.to_csv(os.path.join(output_dir, 'train_metadata.csv'), index=False)
    val_df.to_csv(os.path.join(output_dir, 'val_metadata.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, 'test_metadata.csv'), index=False)
    
    print("Agent Workflow Complete! Data is ready for Label Mapping.")

if __name__ == "__main__":
    # Base directory is v5/data_preparation, so archive is ../../archive
    standardize_and_merge(
        "../../archive/ISIC/ISIC_2019_Training_Metadata.csv",
        "../../archive/ISIC/ISIC_2019_Training_GroundTruth.csv",
        "../../archive/DDI_Dataset/ddi_metadata.csv",
        "../data_preparation/"
    )
