import os

def inject_replay():
    path = "v5/training/dataset.py"
    
    code = """
def create_replay_buffer_generator(standard_csv_path, hard_csv_path, batch_size=16, img_size=(380, 380)):
    \"\"\"
    Continuous Learning Loop implementation.
    Mixes standard historical dataset with hard examples submitted by doctors.
    Enforces a 90/10 split to prevent catastrophic forgetting.
    \"\"\"
    # Create the standard dataset generator (unbatched for sampling)
    standard_ds = create_csv_dataset_generator(standard_csv_path, batch_size=batch_size, img_size=img_size, is_training=True)
    if standard_ds is not None:
        standard_ds = standard_ds.unbatch()
    
    AUTOTUNE = tf.data.AUTOTUNE
    
    if not os.path.exists(hard_csv_path):
        print(f"No hard examples found at {hard_csv_path}. Using standard dataset only.")
        return standard_ds.batch(batch_size).prefetch(AUTOTUNE) if standard_ds else None
        
    df_hard = pd.read_csv(hard_csv_path)
    if len(df_hard) == 0:
        return standard_ds.batch(batch_size).prefetch(AUTOTUNE) if standard_ds else None
        
    print(f"✅ Found {len(df_hard)} hard examples. Activating Replay Buffer (90/10 mix).")
    
    # Construct paths for hard examples
    base_dir = os.path.dirname(__file__)
    df_hard['full_path'] = df_hard['image_id'].apply(lambda x: os.path.abspath(os.path.join(base_dir, "..", "data_preparation", "hard_examples", f"{x}.jpg")))
    
    diag_map = {'mel':0, 'nv':1, 'bcc':2, 'ak':3, 'bkl':4, 'df':5, 'vasc':6, 'scc':7, 'unk':8}
    df_hard['ddx_idx'] = df_hard['diagnosis'].str.lower().map(diag_map).fillna(9).astype(int)
    
    # Map etiology (Melanocytic:0, Epithelial:1, Vascular:2, Other:3)
    etiology_map = {0:0, 1:0, 2:1, 3:1, 4:1, 7:1, 6:2, 5:3, 8:3, 9:3}
    df_hard['etiology_family'] = df_hard['ddx_idx'].map(etiology_map).fillna(3).astype(int)
    
    paths = df_hard['full_path'].values
    ddx_labels = df_hard['ddx_idx'].values
    eti_labels = df_hard['etiology_family'].values
    
    hard_ds = tf.data.Dataset.from_tensor_slices((paths, ddx_labels, eti_labels))
    hard_ds = hard_ds.shuffle(1000).repeat()
    
    hard_ds = hard_ds.map(
        lambda p, d, e: load_and_preprocess_image(p, d, e, img_size=img_size), 
        num_parallel_calls=AUTOTUNE
    )
    
    # Sample from both datasets with 90/10 split
    replay_ds = tf.data.Dataset.sample_from_datasets([standard_ds.repeat(), hard_ds], weights=[0.90, 0.10])
    
    return replay_ds.batch(batch_size).prefetch(buffer_size=AUTOTUNE)
"""
    with open(path, "r") as f:
        content = f.read()
    
    if "def create_replay_buffer_generator" not in content:
        # Insert before if __name__ == "__main__":
        parts = content.split('if __name__ == "__main__":')
        new_content = parts[0] + code + '\nif __name__ == "__main__":' + parts[1]
        with open(path, "w") as f:
            f.write(new_content)
        print("Replay buffer injected successfully!")
    else:
        print("Already injected.")

if __name__ == "__main__":
    inject_replay()
