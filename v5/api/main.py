import os
import io
import sys
import time
import tempfile
import base64
from contextlib import asynccontextmanager

import numpy as np
import cv2
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as preprocess_efficientnet
from tensorflow.keras.applications.resnet_v2 import preprocess_input as preprocess_resnet

from risk_calculator import RiskCalculator
from report_generator import generate_clinical_report, REPORTS_DIR
from gradcam import generate_gradcam, overlay_heatmap

training_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "training"))
sys.path.append(training_dir)
from model import create_v5_dual_head_model
from model_multimodal import create_v5_multimodal_model, create_v5_meta_learner
from custom_model import GradientAccumulationModel

IMAGE_SIZE_A = (380, 380) # EfficientNet
IMAGE_SIZE_B = (380, 380) # ResNet50V2

model_a = None
model_b = None
model_c = None
risk_calculator = RiskCalculator()

SEX_CATEGORIES = ['male', 'female', 'unknown']
SITE_CATEGORIES = ['posterior torso', 'upper extremity', 'lower extremity', 
                   'head/neck', 'anterior torso', 'oral/genital', 
                   'palms/soles', 'lateral torso', 'unknown']

def encode_metadata(age, sex, site):
    """Encodes metadata into a 14-dimensional normalized vector."""
    is_missing = False
    if not age and not sex and not site:
        is_missing = True
        
    if is_missing or age is None or age == "":
        age_norm = 0.0
    else:
        try:
            age_norm = min(float(age) / 100.0, 1.0)
        except:
            age_norm = 0.0
            
    sex_one_hot = [0.0] * len(SEX_CATEGORIES)
    sex = str(sex).lower() if sex else ""
    if is_missing or sex not in SEX_CATEGORIES:
        sex_idx = SEX_CATEGORIES.index('unknown')
    else:
        sex_idx = SEX_CATEGORIES.index(sex)
    sex_one_hot[sex_idx] = 1.0
    
    site_one_hot = [0.0] * len(SITE_CATEGORIES)
    site = str(site).lower() if site else ""
    if is_missing or site not in SITE_CATEGORIES:
        site_idx = SITE_CATEGORIES.index('unknown')
    else:
        site_idx = SITE_CATEGORIES.index(site)
    site_one_hot[site_idx] = 1.0
    
    missing_flag = [1.0 if is_missing else 0.0]
    
    metadata_vector = [age_norm] + sex_one_hot + site_one_hot + missing_flag
    return np.array(metadata_vector, dtype=np.float32)

def load_models():
    global model_a, model_b, model_c
    tf.config.optimizer.set_jit(True)
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "training", "checkpoints"))
    path_a = os.path.join(base_dir, "best_model.keras")
    path_b = os.path.join(base_dir, "best_model_multimodal.h5")
    path_c = os.path.join(base_dir, "best_model_metalearner.h5")
    
    try:
        # Load Model A (Needs Wrapper trick to load weights properly)
        base_a = create_v5_dual_head_model()
        model_a = GradientAccumulationModel(inputs=base_a.inputs, outputs=base_a.outputs, accumulation_steps=4)
        model_a.grad_accumulator = [tf.Variable(tf.zeros_like(var), trainable=False) for var in model_a.trainable_variables]
        model_a.load_weights(path_a)
        print(f"✅ Model A (Vision Expert) loaded", flush=True)
        
        # Load Model B
        model_b = create_v5_multimodal_model()
        model_b.load_weights(path_b)
        print(f"✅ Model B (Multimodal Expert) loaded", flush=True)
        
        # Load Model C
        model_c = create_v5_meta_learner()
        model_c.load_weights(path_c)
        print(f"✅ Model C (Meta-Learner) loaded", flush=True)
        
        # Pre-warm models
        dummy_img = np.zeros((1, 380, 380, 3), dtype=np.float32)
        dummy_meta = np.zeros((1, 14), dtype=np.float32)
        
        preds_a = model_a.predict(dummy_img, verbose=0)
        preds_b = model_b.predict([dummy_img, dummy_meta], verbose=0)
        _ = model_c.predict([preds_a[0], preds_b[0], dummy_meta], verbose=0)
        
        print("✅ All Models pre-warmed.", flush=True)
    except Exception as e:
        print(f"⚠️ Warning: Could not load models. Error: {e}", flush=True)
        model_a = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield

app = FastAPI(
    title="DermaScan AI V5 API",
    description="Multimodal Stacking Ensemble Architecture",
    version="5.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Online", "model": "V5 Ensemble (A+B+C)"}

@app.get("/api/health")
def health():
    return {
        "model_loaded": model_a is not None and model_b is not None and model_c is not None,
        "image_size": list(IMAGE_SIZE_A),
        "architecture": "Multimodal Stacking Ensemble"
    }

@app.post("/api/analyze")
def analyze_lesion(
    file: UploadFile = File(...),
    age: str = Form(None),
    sex: str = Form(None),
    anatom_site: str = Form(None)
):
    start_time = time.time()
    
    if model_c is None:
        raise HTTPException(status_code=503, detail="Models are still training or failed to load.")
        
    try:
        contents = file.file.read()
        image_pil = Image.open(io.BytesIO(contents)).convert("RGB")
        img_cv2 = np.array(image_pil)
        
        # Center Crop to preserve aspect ratio
        h, w = img_cv2.shape[:2]
        min_dim = min(h, w)
        top = (h - min_dim) // 2
        left = (w - min_dim) // 2
        
        img_cropped = img_cv2[top:top+min_dim, left:left+min_dim]
        img_resized = cv2.resize(img_cropped, IMAGE_SIZE_A, interpolation=cv2.INTER_CUBIC)
        
        # Save perfectly scaled 380x380 image for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_orig:
            Image.fromarray(img_resized).save(tmp_orig.name)
            tmp_orig_path = tmp_orig.name
            
        # Create base64 of the cropped image to send to frontend!
        _, buffer_crop = cv2.imencode('.jpg', cv2.cvtColor(img_resized, cv2.COLOR_RGB2BGR))
        cropped_b64 = base64.b64encode(buffer_crop).decode('utf-8')
        
        # --- Metadata Prep ---
        meta_vec = encode_metadata(age, sex, anatom_site)
        meta_input = np.expand_dims(meta_vec, axis=0)
        
        # --- Model A Inference (EfficientNet) ---
        img_a = preprocess_efficientnet(img_resized.astype(np.float32))
        img_input_a = np.expand_dims(img_a, axis=0)
        preds_a = model_a.predict(img_input_a, verbose=0)
        
        # --- Model B Inference (ResNet50V2 + Metadata) ---
        img_b = preprocess_resnet(img_resized.astype(np.float32))
        img_input_b = np.expand_dims(img_b, axis=0)
        preds_b = model_b.predict([img_input_b, meta_input], verbose=0)
        
        # --- Model C Inference (Meta-Learner) ---
        # Note: Model A and B both return [ddx_preds, eti_preds]
        # We only pass the DDX predictions to the MetaLearner
        preds_c = model_c.predict([preds_a[0], preds_b[0], meta_input], verbose=0)
        
        ddx_preds = preds_c[0]       # Shape (10,)
        
        # We still need etiology for the risk calculator, so we just average A and B's etiology
        etiology_preds = (preds_a[1][0] + preds_b[1][0]) / 2.0
        
        # --- HOTFIX for "Other" dominating predictions ---
        # Absolutely zero out "Other" (9) and "Unknown" (8) so they never get predicted.
        ddx_preds[8] = 0.0
        ddx_preds[9] = 0.0
        ddx_sum = np.sum(ddx_preds)
        if ddx_sum > 0:
            ddx_preds = ddx_preds / ddx_sum # re-normalize
        else:
            ddx_preds[1] = 1.0 # NV
        
        result_dict = risk_calculator.calculate_risk(ddx_preds, etiology_preds)
        result_dict["cropped_image"] = f"data:image/jpeg;base64,{cropped_b64}"
        
        # Generate Grad-CAM Heatmap using Model A (Vision Expert)
        top_idx = np.argmax(ddx_preds)
        heatmap_base64 = None
        tmp_heatmap_path = None
        try:
            # We pass the raw (img_resized / 255.0) for overlay so it looks normal colors
            hm_array = generate_gradcam(model_a, img_input_a, top_idx)
            heatmap_base64 = overlay_heatmap(img_resized / 255.0, hm_array)
            result_dict["heatmap"] = heatmap_base64
            
            # Save heatmap for PDF
            hm_data = base64.b64decode(heatmap_base64.split(",")[1])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_hm:
                tmp_hm.write(hm_data)
                tmp_heatmap_path = tmp_hm.name
        except Exception as e:
            print(f"Warning: Grad-CAM failed: {e}", flush=True)
        
        report_id, _ = generate_clinical_report(result_dict, image_path=tmp_orig_path, heatmap_path=tmp_heatmap_path)
        
        analysis_time = time.time() - start_time
        result_dict["analysis_time"] = round(analysis_time, 2)
        result_dict["report_id"] = report_id
        
        os.unlink(tmp_orig_path)
        if tmp_heatmap_path:
            os.unlink(tmp_heatmap_path)
        
        return result_dict
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-report/{report_id}")
def download_report(report_id: str):
    pdf_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"DermaScan_V5_{report_id}.pdf",
        )
    raise HTTPException(status_code=404, detail="Report not found or expired.")

import uuid
from pydantic import BaseModel
import csv

class FeedbackRequest(BaseModel):
    image_b64: str
    original_diagnosis: str
    corrected_diagnosis: str
    age: str
    sex: str
    anatom_site: str

@app.post("/api/submit_feedback")
def submit_feedback(data: FeedbackRequest):
    try:
        # 1. Ensure hard_examples directory exists
        hard_examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_preparation", "hard_examples"))
        os.makedirs(hard_examples_dir, exist_ok=True)
        
        # 2. Save the image
        img_id = f"FEEDBACK_{uuid.uuid4().hex[:8]}"
        img_path = os.path.join(hard_examples_dir, f"{img_id}.jpg")
        
        # Strip the base64 header if present
        b64_str = data.image_b64
        if b64_str.startswith("data:image"):
            b64_str = b64_str.split(",")[1]
            
        img_data = base64.b64decode(b64_str)
        with open(img_path, "wb") as f:
            f.write(img_data)
            
        # 3. Append to CSV
        csv_path = os.path.abspath(os.path.join(hard_examples_dir, "..", "hard_examples_metadata.csv"))
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["image_id", "diagnosis", "age", "sex", "anatom_site"])
            writer.writerow([img_id, data.corrected_diagnosis.lower(), data.age, data.sex, data.anatom_site])
            
        return {"status": "success", "message": f"Saved {img_id} to replay buffer."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Feedback loop failed: {str(e)}")
