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
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input

from risk_calculator import RiskCalculator
from report_generator import generate_clinical_report, REPORTS_DIR
from gradcam import generate_gradcam, overlay_heatmap

training_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "training"))
sys.path.append(training_dir)
from model import create_v5_dual_head_model

IMAGE_SIZE = (380, 380)

model = None
risk_calculator = RiskCalculator()

def load_model():
    global model
    tf.config.optimizer.set_jit(True)
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "training", "checkpoints"))
    model_path = os.path.join(base_dir, "best_model.h5")
    
    try:
        model = create_v5_dual_head_model()
        model.load_weights(model_path, by_name=True, skip_mismatch=True)
        print(f"✅ V5 Model loaded: {model_path}", flush=True)
        
        dummy_img = np.zeros((1, 380, 380, 3), dtype=np.float32)
        model.predict(dummy_img, verbose=0)
        print("✅ Model pre-warmed.", flush=True)
    except Exception as e:
        print(f"⚠️ Warning: Could not load model from {model_path}. Is it done training? Error: {e}", flush=True)
        model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(
    title="DermaScan AI V5 API",
    description="Dual-Head Image-Only Architecture",
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
    return {"status": "Online", "model": "V5 Dual-Head (Image-Only)"}

@app.get("/api/health")
def health():
    return {
        "model_loaded": model is not None,
        "image_size": list(IMAGE_SIZE),
        "architecture": "Dual-Head (DDx + Etiology)"
    }

@app.post("/api/analyze")
def analyze_lesion(file: UploadFile = File(...)):
    start_time = time.time()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model is still training or failed to load.")
        
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
        img_resized = cv2.resize(img_cropped, IMAGE_SIZE, interpolation=cv2.INTER_CUBIC)
        
        # Save perfectly scaled 380x380 image for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_orig:
            Image.fromarray(img_resized).save(tmp_orig.name)
            tmp_orig_path = tmp_orig.name
            
        # Create base64 of the cropped image to send to frontend!
        _, buffer_crop = cv2.imencode('.jpg', cv2.cvtColor(img_resized, cv2.COLOR_RGB2BGR))
        cropped_b64 = base64.b64encode(buffer_crop).decode('utf-8')
        
        img_normalized = preprocess_input(img_resized.astype(np.float32))
        img_input = np.expand_dims(img_normalized, axis=0)
        
        preds = model.predict(img_input, verbose=0)
        ddx_preds = preds[0][0]       # Shape (10,)
        etiology_preds = preds[1][0]  # Shape (4,)
        
        # --- HOTFIX for "Other" dominating predictions ---
        # Absolutely zero out "Other" (9) and "Unknown" (8) so they never get predicted.
        ddx_preds[8] = 0.0
        ddx_preds[9] = 0.0
        ddx_sum = np.sum(ddx_preds)
        if ddx_sum > 0:
            ddx_preds = ddx_preds / ddx_sum # re-normalize
        else:
            # Fallback if somehow everything was 0 (impossible, but safe)
            ddx_preds[1] = 1.0 # NV
        
        result_dict = risk_calculator.calculate_risk(ddx_preds, etiology_preds)
        result_dict["cropped_image"] = f"data:image/jpeg;base64,{cropped_b64}"
        
        # Generate Grad-CAM Heatmap for the top DDX predicted class!
        top_idx = np.argmax(ddx_preds)
        heatmap_base64 = None
        tmp_heatmap_path = None
        try:
            # We pass the raw (img_resized / 255.0) for overlay so it looks normal colors
            hm_array = generate_gradcam(model, img_input, top_idx)
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
