import streamlit as st
import numpy as np
import pandas as pd
import cv2
import pickle
from PIL import Image
import tensorflow as tf

# Performance Optimization: Enable XLA JIT Compilation
tf.config.optimizer.set_jit(True)
from fpdf import FPDF
import tempfile
import os
import hashlib
import requests
from streamlit_lottie import st_lottie

from safety_net import validate_input, check_skin_lesion, log_prediction
from clinical_mapper import map_prediction, CLASS_NAMES
from gradcam import generate_gradcam, overlay_heatmap

# Constants
IMAGE_SIZE = (224, 224)

# Page config
st.set_page_config(page_title="DermaScan AI V3", layout="wide", page_icon="🔬")

# Load CSS
def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Always-visible disclaimer banner
st.markdown('''
<div class="disclaimer-banner">
    ⚠️ ACADEMIC PROTOTYPE – Not for clinical use. This tool is designed to assist, not replace, a medical professional.
</div>
''', unsafe_allow_html=True)

@st.cache_resource
def load_objects():
    try:
        with open("preprocessing_objects.pkl", "rb") as f:
            objs = pickle.load(f)
    except FileNotFoundError:
        objs = None
        
    try:
        model = tf.keras.models.load_model("dermascan_v3_best.keras")
        # Pre-warm model for XLA compilation
        dummy_img = np.zeros((1, 224, 224, 3), dtype=np.float32)
        dummy_meta = np.zeros((1, 10), dtype=np.float32)
        model.predict([dummy_img, dummy_meta], verbose=0)
    except Exception:
        model = None
    return objs, model

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

objs, model = load_objects()
lottie_medical = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_5njp3vgg.json")

# Sidebar
st.sidebar.title(":material/person: Patient Information")
uploaded_file = st.sidebar.file_uploader("Upload Lesion Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
age = st.sidebar.number_input("Patient Age", min_value=0, max_value=120, value=50, step=1)
sex = st.sidebar.selectbox("Sex", ["Female", "Male"])
site_options = ["Anterior torso", "Head/neck", "Lateral torso", "Lower extremity", "Oral/genital", "Palms/soles", "Posterior torso", "Upper extremity"]
site = st.sidebar.selectbox("Anatomical Site", site_options)

st.sidebar.markdown("---")
demo_mode = st.sidebar.checkbox("Demo Mode", value=False, help="Lowers uncertainty threshold to 0.5 for presentation purposes.")

st.title(":material/health_and_safety: DermaScan AI V3 Clinical Decision Support")

if uploaded_file is not None:
    # Save to temp file for safety_net validation
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
        
    if st.button("Analyze Lesion"):
        # 1. Safety net
        if not validate_input(tmp_path):
            st.error("Validation Failed: Please upload a valid JPEG/PNG image (minimum 224x224).")
            st.stop()
            
        image_pil = Image.open(uploaded_file).convert("RGB")
        img_cv2 = np.array(image_pil)
        
        if not check_skin_lesion(img_cv2):
            st.warning("Warning: The image variance is low. This may not be a skin lesion. Proceeding with caution.")
            
        if model is None or objs is None:
            st.error("Model or preprocessing objects not found. Please train the model first.")
            st.stop()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(":material/image: Original Image")
            # Will be updated to preprocessed image once we have img_resized

        with st.spinner("Analyzing..."):
            if lottie_medical:
                st_lottie(lottie_medical, height=150, key="loading")
                
            # 2. Preprocess
            img_resized = cv2.resize(img_cv2, IMAGE_SIZE)
            img_normalized = img_resized.astype(np.float32)
            
            # Update col1 with preprocessed image for 1:1 alignment
            with col1:
                st.image(img_resized.astype(np.uint8), caption="Preprocessed Input (224x224)", use_container_width=True)
                
            # ---------- V2 metadata construction (10 features) ----------
            v2_site_columns = [
                'site_anterior torso',
                'site_head/neck',
                'site_lateral torso',
                'site_lower extremity',
                'site_oral/genital',
                'site_palms/soles',
                'site_posterior torso',
                'site_upper extremity'
            ]

            # V2 age normalization: z-score using mean and std from V2 training set
            AGE_MEAN = 54.58772832518652
            AGE_STD = 18.188632571786233
            age_scaled = (age - AGE_MEAN) / AGE_STD

            # Sex encoding: V2 used female=1, male=0
            if sex == 'Female':
                sex_encoded = 1.0
            else:
                sex_encoded = 0.0

            # One-hot encode anatomical site for V2's 8 categories
            site_encoded = np.zeros(len(v2_site_columns), dtype=np.float32)
            # Map display name back to internal key
            site_key = f"site_{site.lower()}"
            if site_key in v2_site_columns:
                idx = v2_site_columns.index(site_key)
                site_encoded[idx] = 1.0
            # If site not in list (e.g., "unknown"), leave all zeros

            # Build the final 10-element metadata vector
            meta_features = np.concatenate([
                [age_scaled],
                [sex_encoded],
                site_encoded
            ]).astype(np.float32).reshape(1, -1)  # shape (1, 10)
            # 3. Model Prediction
            img_input = np.expand_dims(img_normalized, axis=0)
            preds = model.predict([img_input, meta_features])
            
            pred_idx = np.argmax(preds[0])
            confidence = float(preds[0][pred_idx])
            
            # Map V2 index to ISIC abbreviation
            v2_to_isic = {0: 'NV', 1: 'MEL', 2: 'BKL', 3: 'DF', 4: 'SCC', 5: 'BCC', 6: 'VASC', 7: 'AK'}
            isic_abbr = v2_to_isic[pred_idx]
            
            # 4. Clinical Mapper
            mapping = map_prediction(isic_abbr, confidence, demo_mode=demo_mode)
            
            # 5. Grad-CAM (with fallback if layer not found)
            try:
                heatmap = generate_gradcam(model, img_normalized, pred_idx)
                overlay = overlay_heatmap(img_normalized / 255.0, heatmap)
            except Exception as e:
                st.warning(f"Grad‑CAM visualization unavailable: {e}")
                # Create a simple placeholder overlay (original image slightly dimmed)
                overlay = (img_normalized / 255.0 * 0.7).astype(np.float32)
            
            # Save for report
            st.session_state['analysis_done'] = True
            st.session_state['overlay'] = overlay
            st.session_state['mapping'] = mapping
            st.session_state['preds'] = preds[0]
            st.session_state['img_cv2'] = img_cv2
            st.session_state['metadata'] = {"age": age, "sex": sex, "site": site}
            
            # Safety Log
            img_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
            log_prediction(None, img_hash, st.session_state['metadata'], 
                           {'predicted_class': mapping['class_name'], 'confidence': confidence, 'risk_group': mapping['risk_group']})
            
        with col2:
            st.subheader(":material/center_focus_strong: Grad-CAM Overlay")
            st.image(overlay, use_container_width=True)
            
        # Display Results
        st.markdown(f"""
        <div class="clinical-card" style="background-color: {mapping['risk_color']}; color: {'#000' if mapping['risk_color'] in ['yellow', 'green'] else '#fff'};">
            <h3>Diagnostic Interpretation: {mapping['class_full']}</h3>
            <p><strong>Risk Group:</strong> {mapping['risk_group']}</p>
            <p><strong>Confidence:</strong> {confidence:.2%}</p>
            <p><strong>Recommendation:</strong> {mapping['recommendation']}</p>
            <p><em>{mapping['explanation']}</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader(":material/bar_chart: Differential Diagnosis Probabilities")
        probs_by_abbr = {v2_to_isic[i]: float(p) for i, p in enumerate(preds[0])}
        reordered_probs = [probs_by_abbr[cls] for cls in CLASS_NAMES]
        prob_df = pd.DataFrame({"Class": CLASS_NAMES, "Probability": reordered_probs})
        st.bar_chart(prob_df.set_index("Class"))

if st.session_state.get('analysis_done', False):
    if st.button("Generate Clinical Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        pdf.cell(190, 10, txt="DermaScan AI V3 - Clinical Report", ln=True, align="C")
        pdf.ln(10)
        
        mapping = st.session_state['mapping']
        meta = st.session_state['metadata']
        
        pdf.set_font("Arial", size=12)
        pdf.cell(190, 10, txt=f"Patient Age: {meta['age']}, Sex: {meta['sex'].capitalize()}, Site: {meta['site'].capitalize()}", ln=True)
        pdf.cell(190, 10, txt=f"Primary Diagnosis: {mapping['class_full']} ({mapping['risk_group']})", ln=True)
        pdf.cell(190, 10, txt=f"Recommendation: {mapping['recommendation']}", ln=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp1:
            Image.fromarray(st.session_state['img_cv2']).save(tmp1.name)
            pdf.image(tmp1.name, x=10, y=70, w=85)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp2:
            Image.fromarray(st.session_state['overlay']).save(tmp2.name)
            pdf.image(tmp2.name, x=105, y=70, w=85)
            
        pdf.set_y(170)
        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 10, txt="WARNING: ACADEMIC PROTOTYPE - Not for clinical use. This tool is designed to assist, not replace, a medical professional.")
        
        pdf_file = "clinical_report.pdf"
        pdf.output(pdf_file)
        
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF Report", f, file_name="clinical_report.pdf")
