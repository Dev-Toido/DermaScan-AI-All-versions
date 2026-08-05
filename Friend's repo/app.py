import os
import io
import time
import base64
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from train_new_architecture import DermaScanDenseNet

app = FastAPI(title="DermaScan AI API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": "DermaScan AI API is running! The AI engine is waiting for images.",
        "frontend": "Please open http://localhost:3000 in your browser to use the interface."
    }

CLASSES = [
    'Actinic Keratosis', 
    'Basal Cell Carcinoma', 
    'Benign Keratosis', 
    'Dermatofibroma', 
    'Melanoma', 
    'Melanocytic Nevi', 
    'Vascular Lesion'
]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- NEW DENSENET FINETUNED MODEL ---
model = DermaScanDenseNet(num_classes=len(CLASSES), freeze_base=True)
model_path = os.path.join('models', 'dermascan_densenet_finetuned.pth')

if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    print("Model loaded successfully!")
else:
    print(f"WARNING: Could not find '{model_path}'")

transform = transforms.Compose([
    transforms.Resize((380, 380)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# --- Grad-CAM Implementation ---
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        target_layer.register_forward_hook(self.save_activation)
        target_layer.register_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_cam(self, input_tensor, target_class=None):
        self.model.eval()
        
        # Forward pass
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = output.argmax(dim=1).item()
            
        self.model.zero_grad()
        target = output[0][target_class]
        target.backward(retain_graph=True)
        
        # Get pooled gradients
        gradients = self.gradients.cpu().data.numpy()[0]
        activations = self.activations.cpu().data.numpy()[0]
        
        weights = np.mean(gradients, axis=(1, 2))
        
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
            
        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (input_tensor.shape[3], input_tensor.shape[2]))
        cam = cam - np.min(cam)
        cam = cam / np.max(cam)
        
        return cam

# Initialize Grad-CAM on the last feature layer of EfficientNet
# Base model is efficientnet_b4, the features are in model.base_model.features
try:
    target_layer = model.base_model.features[-1]
    cam_extractor = GradCAM(model, target_layer)
except Exception as e:
    print("Error setting up GradCAM:", e)
    cam_extractor = None

def analyze_risk_and_confidence(probabilities):
    # Find the top prediction
    top_prob = max(probabilities)
    top_idx = list(probabilities).index(top_prob)
    top_class = CLASSES[top_idx]
    
    # Define Risk Categories
    high_risk_classes = ['Melanoma', 'Basal Cell Carcinoma']
    
    # 1. Check Confidence Thresholds
    if top_prob < 0.50:
        risk_group = "Uncertain"
        recommendation = "Insufficient confidence. Consult a dermatologist."
        status = "The model's confidence is too low to provide a definitive prediction. Clinical evaluation is strongly advised."
    
    # 2. Check for High-Risk Cancers
    elif top_class in high_risk_classes:
        risk_group = "High Risk"
        recommendation = "Urgent clinical evaluation required."
        status = "The AI detected visual patterns consistent with skin cancer. Please seek medical attention immediately."
        
    # 3. Check for False Alarms (High risk classes hiding in 2nd place)
    else:
        # Check if Melanoma or BCC is lurking above 15% even if it's not the top prediction
        melanoma_idx = CLASSES.index('Melanoma')
        bcc_idx = CLASSES.index('Basal Cell Carcinoma')
        
        if probabilities[melanoma_idx] > 0.15 or probabilities[bcc_idx] > 0.15:
            risk_group = "Elevated Risk"
            recommendation = "Monitor closely. High-risk features detected."
            status = "The AI primarily suspects a benign lesion, but detected secondary patterns commonly found in skin cancers."
        else:
            risk_group = "Low Risk"
            recommendation = "Routine monitoring."
            status = "The AI detected patterns consistent with a benign (harmless) skin lesion."

    return {
        "top_diagnosis": top_class,
        "confidence_percentage": round(top_prob * 100, 2),
        "risk_group": risk_group,
        "recommendation": recommendation,
        "status": status
    }

@app.post("/api/analyze")
async def analyze_lesion(file: UploadFile = File(...)):
    start_time = time.time()
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    original_size = image.size
    
    input_tensor = transform(image).unsqueeze(0).to(device)
    input_tensor.requires_grad = True # Required for Grad-CAM
    
    # Run Inference
    output = model(input_tensor)
    probabilities = F.softmax(output[0], dim=0).detach().cpu().numpy()
    
    results = {CLASSES[i]: float(probabilities[i]) for i in range(len(CLASSES))}
    
    # Merge Seborrheic Keratosis into Benign Keratosis
    if 'Seborrheic Keratosis' in results and 'Benign Keratosis' in results:
        results['Benign Keratosis'] += results['Seborrheic Keratosis']
        del results['Seborrheic Keratosis']
        
    risk_analysis = analyze_risk_and_confidence(probabilities)
    
    heatmap_base64 = None
    if cam_extractor:
        cam = cam_extractor.generate_cam(input_tensor)
        
        # Convert original image to cv2 format
        img_np = np.array(image.resize((380, 380)))
        img_np = img_np[:, :, ::-1].copy() # RGB to BGR
        
        # Apply colormap
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = np.float32(heatmap) / 255
        
        # Overlay
        overlay = heatmap * 0.4 + np.float32(img_np) / 255 * 0.6
        overlay = overlay / np.max(overlay)
        
        # Convert back to PIL for encoding
        overlay_uint8 = np.uint8(255 * overlay)
        overlay_rgb = cv2.cvtColor(overlay_uint8, cv2.COLOR_BGR2RGB)
        overlay_img = Image.fromarray(overlay_rgb).resize(original_size)
        
        buffered = io.BytesIO()
        overlay_img.save(buffered, format="JPEG", quality=90)
        heatmap_base64 = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    analysis_time = time.time() - start_time
    
    return {
        "probabilities": results,
        "top_diagnosis": risk_analysis["top_diagnosis"],
        "confidence": f"{risk_analysis['confidence_percentage']}%",
        "risk_group": risk_analysis["risk_group"],
        "recommendation": risk_analysis["recommendation"],
        "status_message": risk_analysis["status"],
        "analysis_time": round(analysis_time, 2),
        "heatmap": heatmap_base64
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
