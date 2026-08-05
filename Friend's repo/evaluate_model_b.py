import os
import time
import torch
import pandas as pd
import numpy as np
from PIL import Image
from torchvision import transforms
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import sys

# Import the model architecture
from train_new_architecture import DermaScanDenseNet

def main():
    CSV_PATH = 'balanced_test/balanced_test.csv'
    IMG_DIR = 'balanced_test/images'
    OUT_PATH = 'balanced_test/model_b_results.txt'
    MODEL_PATH = 'models/dermascan_densenet_finetuned.pth'
    
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Initialize and load model
    print(f"Loading model from {MODEL_PATH}...")
    # Model B has 7 classes
    model = DermaScanDenseNet(num_classes=7, freeze_base=True)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    else:
        print(f"Error: {MODEL_PATH} not found.")
        sys.exit(1)
        
    model.to(device)
    model.eval()
    
    # Preprocessing
    transform = transforms.Compose([
        transforms.Resize((380, 380)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Mapping
    # Model B outputs:
    # 0: Actinic Keratosis -> AK
    # 1: Basal Cell Carcinoma -> BCC
    # 2: Benign Keratosis -> BKL
    # 3: Dermatofibroma -> DF
    # 4: Melanoma -> MEL
    # 5: Melanocytic Nevi -> NV
    # 6: Vascular Lesion -> VASC
    MODEL_B_OUTPUT_ORDER = {
        0: 'AK', 1: 'BCC', 2: 'BKL', 3: 'DF', 4: 'MEL', 5: 'NV', 6: 'VASC'
    }
    STANDARD_MAP = {'MEL':0, 'NV':1, 'BCC':2, 'AK':3, 'BKL':4, 'DF':5, 'VASC':6, 'SCC':7}
    
    y_true = []
    y_pred = []
    inference_times = []
    
    print("Running inference...")
    for i, row in df.iterrows():
        img_name = row['image']
        img_path = os.path.join(IMG_DIR, f"{img_name}.jpg")
        
        try:
            image = Image.open(img_path).convert("RGB")
        except FileNotFoundError:
            print(f"File not found: {img_path}")
            continue
            
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        start_time = time.time()
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            pred_idx = probabilities.argmax().item()
        inf_time = time.time() - start_time
        inference_times.append(inf_time)
        
        isic_abbr = MODEL_B_OUTPUT_ORDER[pred_idx]
        standard_idx = STANDARD_MAP[isic_abbr]
        
        y_true.append(row['label'])
        y_pred.append(standard_idx)
        
        if (i+1) % 50 == 0:
            print(f"Processed {i+1}/{len(df)} images...")
            
    avg_time = np.mean(inference_times)
    acc = accuracy_score(y_true, y_pred)
    target_names = ['MEL', 'NV', 'BCC', 'AK', 'BKL', 'DF', 'VASC', 'SCC']
    
    # In case there are labels that are never predicted, suppress warnings
    import warnings
    from sklearn.exceptions import UndefinedMetricWarning
    warnings.filterwarnings("ignore", category=UndefinedMetricWarning)
    
    report = classification_report(y_true, y_pred, target_names=target_names, labels=[0,1,2,3,4,5,6,7])
    
    cm = confusion_matrix(y_true, y_pred, labels=[0,1,2,3,4,5,6,7])
    sens_mel = cm[0,0] / np.sum(cm[0,:]) if np.sum(cm[0,:]) > 0 else 0
    sens_bcc = cm[2,2] / np.sum(cm[2,:]) if np.sum(cm[2,:]) > 0 else 0
    sens_scc = cm[7,7] / np.sum(cm[7,:]) if np.sum(cm[7,:]) > 0 else 0
    
    output = f"Accuracy: {acc:.4f}\n"
    output += f"Average Inference Time: {avg_time:.4f} seconds/image\n\n"
    output += "Sensitivity for Malignant Classes:\n"
    output += f"- MEL (Melanoma): {sens_mel:.4f}\n"
    output += f"- BCC (Basal Cell Carcinoma): {sens_bcc:.4f}\n"
    output += f"- SCC (Squamous Cell Carcinoma): {sens_scc:.4f} (Note: Model does not predict SCC)\n\n"
    output += "Classification Report:\n"
    output += report

    with open(OUT_PATH, 'w') as f:
        f.write(output)

    print(f"Evaluation complete. Results saved to {OUT_PATH}")

if __name__ == "__main__":
    main()
