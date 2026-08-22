import os

def fix_file(path):
    with open(path, 'r') as f:
        text = f.read()
    
    target = 'base_archive_path="../../archive"'
    replacement = 'base_archive_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "archive"))'
    text = text.replace(target, replacement)
    
    with open(path, 'w') as f:
        f.write(text)

fix_file('v5/training/dataset.py')
fix_file('v5/training/dataset_multimodal.py')
print("Paths fixed successfully.")
