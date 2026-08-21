import pandas as pd

def map_labels_to_etiology_families(unified_csv_path, output_csv_path):
    """
    Maps highly specific disease labels from diverse datasets into broad 
    Etiology Categories for the Etiology Category Head (OOD Safety Net).
    
    Families:
    0: Melanocytic (Melanoma, Nevus)
    1: Keratinocytic (BCC, SCC, AK, BKL)
    2: Vascular (VASC)
    3: Inflammatory/Infectious (Eczema, Psoriasis, etc. - mostly from Diverse datasets)
    """
    print("Agent [Label Mapper]: Analyzing diagnostic labels...")
    try:
        df = pd.read_csv(unified_csv_path)
    except FileNotFoundError:
        print("Awaiting merged dataset.")
        return
        
    # Dictionary Mapping specific diagnoses to etiology index
    # (This will be heavily expanded once the full dataset is downloaded)
    etiology_map = {
        'melanoma': 0,
        'nevus': 0,
        'NV': 0,
        'MEL': 0,
        'basal cell carcinoma': 1,
        'squamous cell carcinoma': 1,
        'actinic keratosis': 1,
        'benign keratosis': 1,
        'BCC': 1,
        'SCC': 1,
        'AK': 1,
        'BKL': 1,
        'vascular lesion': 2,
        'VASC': 2,
        'dermatofibroma': 1,
        'DF': 1,
        # Diverse/Indian dataset specific Inflammatory labels:
        'eczema': 3,
        'psoriasis': 3,
        'fungal infection': 3,
        'acne': 3
    }
    
    def get_etiology(diagnosis):
        diag_lower = str(diagnosis).lower().strip()
        # Fallback to Inflammatory (3) if unknown, to catch OOD safely
        return etiology_map.get(diag_lower, etiology_map.get(diagnosis, 3))
        
    df['etiology_family'] = df['diagnosis'].apply(get_etiology)
    
    df.to_csv(output_csv_path, index=False)
    print(f"Etiology mapping complete. Saved to {output_csv_path}")

if __name__ == "__main__":
    map_labels_to_etiology_families("train_metadata.csv", "train_mapped.csv")
    map_labels_to_etiology_families("val_metadata.csv", "val_mapped.csv")
    map_labels_to_etiology_families("test_metadata.csv", "test_mapped.csv")
