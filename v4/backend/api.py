"""
DermaScan AI V4 — FastAPI Backend
==================================
Uses V3's proven TensorFlow/Keras pipeline:
  - Model: dermascan_v3_best.keras (EfficientNetB4, multi-modal)
  - Preprocessing: 224×224, no pixel normalization, V2 metadata vector
  - Clinical mapper, Grad-CAM, safety net, audit logging, PDF reports
"""

import os
import io
import time
import base64
import hashlib
import tempfile
from contextlib import asynccontextmanager

import numpy as np
import cv2
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ── V3 Imports (unchanged modules) ──────────────────────────────────────────
from safety_net import validate_input, check_skin_lesion, log_prediction
from clinical_mapper import map_prediction, CLASS_NAMES, CLASS_FULL_NAMES
from gradcam import generate_gradcam, overlay_heatmap

# ── Constants (exact V3 values) ─────────────────────────────────────────────
IMAGE_SIZE = (224, 224)
AGE_MEAN = 54.58772832518652
AGE_STD = 18.188632571786233

V2_SITE_COLUMNS = [
    'site_anterior torso',
    'site_head/neck',
    'site_lateral torso',
    'site_lower extremity',
    'site_oral/genital',
    'site_palms/soles',
    'site_posterior torso',
    'site_upper extremity',
]

V2_TO_ISIC = {0: 'NV', 1: 'MEL', 2: 'BKL', 3: 'DF', 4: 'SCC', 5: 'BCC', 6: 'VASC', 7: 'AK'}

SITE_OPTIONS = [
    "Anterior torso", "Head/neck", "Lateral torso", "Lower extremity",
    "Oral/genital", "Palms/soles", "Posterior torso", "Upper extremity",
]

# ── Global State ────────────────────────────────────────────────────────────
model = None
objs = None
last_pdf_path = None  # Stores the path to the most recently generated PDF


def load_model_and_objects():
    """Load V3 model and preprocessing objects, pre-warm for fast first inference."""
    global model, objs
    import tensorflow as tf
    tf.config.optimizer.set_jit(True)

    import pickle

    # Base path is the repo root (since this script runs from v4/backend)
    # Actually, if run from v4/backend, we should compute absolute paths relative to api.py
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "v3"))

    # Load preprocessing objects
    prep_path = os.path.join(base_dir, "preprocessing_objects.pkl")
    try:
        with open(prep_path, "rb") as f:
            objs = pickle.load(f)
        print("✅ Preprocessing objects loaded.")
    except FileNotFoundError:
        print(f"⚠️ {prep_path} not found.")
        objs = None

    # Load model
    model_path = os.path.join(base_dir, "dermascan_v3_best.keras")
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"✅ Model loaded: {model_path}")

        # Pre-warm model for XLA JIT compilation (avoids first-click lag)
        dummy_img = np.zeros((1, 224, 224, 3), dtype=np.float32)
        dummy_meta = np.zeros((1, 10), dtype=np.float32)
        model.predict([dummy_img, dummy_meta], verbose=0)
        print("✅ Model pre-warmed (XLA compiled).")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup."""
    load_model_and_objects()
    yield


# ── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="DermaScan AI V4 API",
    description="Clinical Decision Support — EfficientNetB4 Multi-Modal Pipeline",
    version="4.0.0",
    lifespan=lifespan,
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "Online",
        "message": "DermaScan AI V4 API is running!",
        "model": "EfficientNetB4 (multi-modal, TensorFlow/Keras)",
        "frontend": "Open http://localhost:3000 to use the interface.",
    }


@app.get("/api/health")
def health():
    return {
        "model_loaded": model is not None,
        "preprocessing_loaded": objs is not None,
        "classes": CLASS_NAMES,
        "class_names": CLASS_FULL_NAMES,
        "sites": SITE_OPTIONS,
        "metadata_features": 10,
        "image_size": list(IMAGE_SIZE),
    }


@app.post("/api/analyze")
async def analyze_lesion(
    file: UploadFile = File(...),
    age: int = Form(50),
    sex: str = Form("Female"),
    site: str = Form("Anterior torso"),
    demo_mode: str = Form("false"),
):
    """
    Main analysis endpoint. Runs V3's full pipeline:
    validation → preprocess → predict → clinical map → Grad-CAM → audit log → PDF
    """
    global last_pdf_path
    start_time = time.time()

    if model is None or objs is None:
        raise HTTPException(status_code=503, detail="Model or preprocessing objects not loaded.")

    is_demo = demo_mode.lower() == "true"

    # ── 1. Read and validate image ──────────────────────────────────────────
    contents = await file.read()
    image_hash = hashlib.sha256(contents).hexdigest()

    # Save to temp file for safety_net validation
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    if not validate_input(tmp_path):
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Validation failed: upload a valid JPEG/PNG (minimum 224×224).")

    # ── 2. Open image ───────────────────────────────────────────────────────
    image_pil = Image.open(io.BytesIO(contents)).convert("RGB")
    img_cv2 = np.array(image_pil)

    skin_lesion_ok = check_skin_lesion(img_cv2)

    # ── 3. Preprocess image (exact V3 logic) ────────────────────────────────
    img_resized = cv2.resize(img_cv2, IMAGE_SIZE)
    img_normalized = img_resized.astype(np.float32)  # NO /255 normalization

    # ── 4. Build V2 metadata vector (10 features) ──────────────────────────
    age_scaled = (age - AGE_MEAN) / AGE_STD

    sex_encoded = 1.0 if sex == "Female" else 0.0

    site_encoded = np.zeros(len(V2_SITE_COLUMNS), dtype=np.float32)
    site_key = f"site_{site.lower()}"
    if site_key in V2_SITE_COLUMNS:
        idx = V2_SITE_COLUMNS.index(site_key)
        site_encoded[idx] = 1.0

    meta_features = np.concatenate([
        [age_scaled],
        [sex_encoded],
        site_encoded,
    ]).astype(np.float32).reshape(1, -1)  # shape (1, 10)

    # ── 5. Model prediction ─────────────────────────────────────────────────
    img_input = np.expand_dims(img_normalized, axis=0)
    preds = model.predict([img_input, meta_features], verbose=0)

    pred_idx = int(np.argmax(preds[0]))
    confidence = float(preds[0][pred_idx])

    # Map V2 index → ISIC abbreviation
    isic_abbr = V2_TO_ISIC[pred_idx]

    # ── 6. Clinical mapper ──────────────────────────────────────────────────
    mapping = map_prediction(isic_abbr, confidence, demo_mode=is_demo)

    # ── 7. Grad-CAM ────────────────────────────────────────────────────────
    heatmap_base64 = None
    try:
        heatmap = generate_gradcam(model, img_normalized, pred_idx, meta_features)
        overlay = overlay_heatmap(img_normalized / 255.0, heatmap)

        # Encode overlay to base64 JPEG
        overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB) if overlay.shape[-1] == 3 else overlay
        overlay_pil = Image.fromarray(overlay_rgb if overlay.dtype == np.uint8 else np.uint8(overlay * 255))
        buffered = io.BytesIO()
        overlay_pil.save(buffered, format="JPEG", quality=90)
        heatmap_base64 = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Grad-CAM visualization unavailable: {e}")

    # ── 8. Audit logging ────────────────────────────────────────────────────
    metadata = {"age": age, "sex": sex, "site": site}
    log_prediction(
        None, image_hash, metadata,
        {
            "predicted_class": mapping["class_name"],
            "confidence": confidence,
            "risk_group": mapping["risk_group"],
        },
    )

    # ── 9. PDF report generation ────────────────────────────────────────────
    pdf_available = False
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, txt="DermaScan AI V4 - Clinical Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(190, 10, txt=f"Patient Age: {age}, Sex: {sex}, Site: {site}", ln=True)
        pdf.cell(190, 10, txt=f"Primary Diagnosis: {mapping['class_full']} ({mapping['risk_group']})", ln=True)
        pdf.cell(190, 10, txt=f"Confidence: {confidence:.2%}", ln=True)
        pdf.cell(190, 10, txt=f"Recommendation: {mapping['recommendation']}", ln=True)
        pdf.ln(5)

        # Save original image to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_orig:
            Image.fromarray(img_cv2).save(tmp_orig.name)
            pdf.image(tmp_orig.name, x=10, y=80, w=85)

        # Save Grad-CAM overlay to temp
        if heatmap_base64:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_overlay:
                overlay_pil.save(tmp_overlay.name)
                pdf.image(tmp_overlay.name, x=105, y=80, w=85)

        pdf.set_y(180)
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(
            0, 10,
            txt="WARNING: ACADEMIC PROTOTYPE - Not for clinical use. "
                "This tool is designed to assist, not replace, a medical professional.",
        )

        # All probabilities
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, txt="Differential Diagnosis Probabilities:", ln=True)
        pdf.set_font("Arial", size=11)
        probs_by_abbr = {V2_TO_ISIC[i]: float(p) for i, p in enumerate(preds[0])}
        for cls in CLASS_NAMES:
            full_name = CLASS_FULL_NAMES.get(cls, cls)
            prob = probs_by_abbr.get(cls, 0.0)
            pdf.cell(190, 8, txt=f"  {cls} ({full_name}): {prob:.2%}", ln=True)

        pdf_path = os.path.join(tempfile.gettempdir(), "dermascan_v4_report.pdf")
        pdf.output(pdf_path)
        last_pdf_path = pdf_path
        pdf_available = True
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")

    # ── 10. Build response ──────────────────────────────────────────────────
    analysis_time = time.time() - start_time

    # Build probability dict with ISIC abbreviations as keys
    probabilities = {}
    for i, p in enumerate(preds[0]):
        abbr = V2_TO_ISIC[i]
        full_name = CLASS_FULL_NAMES.get(abbr, abbr)
        probabilities[full_name] = float(p)

    is_uncertain = mapping["risk_group"] == "Uncertain"

    # Clean up temp input file
    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    return {
        "probabilities": probabilities,
        "top_diagnosis": mapping["class_full"],
        "top_abbreviation": mapping["class_name"],
        "confidence": f"{confidence * 100:.1f}%",
        "confidence_raw": confidence,
        "risk_group": mapping["risk_group"],
        "risk_color": mapping["risk_color"],
        "recommendation": mapping["recommendation"],
        "status_message": mapping["explanation"],
        "analysis_time": round(analysis_time, 2),
        "heatmap": heatmap_base64,
        "is_uncertain": is_uncertain,
        "skin_lesion_warning": not skin_lesion_ok,
        "pdf_available": pdf_available,
    }


@app.get("/api/download-report")
def download_report():
    """Download the most recently generated clinical PDF report."""
    if last_pdf_path and os.path.exists(last_pdf_path):
        return FileResponse(
            last_pdf_path,
            media_type="application/pdf",
            filename="DermaScan_V4_Clinical_Report.pdf",
        )
    raise HTTPException(status_code=404, detail="No report available. Run an analysis first.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
