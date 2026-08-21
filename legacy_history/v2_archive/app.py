import os
import streamlit as st
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image

# --- SILENCE TF WARNINGS ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DermaScan AI | Clinical Suite", page_icon="🔬", layout="wide")

# --- CUSTOM CSS (HIDE BRANDING & POLISH) ---
hide_streamlit_style = """
<style>
/* Hide the top right menu and deploy button */
#MainMenu {visibility: hidden;}
.stDeployButton {display: none;}

/* Hide the header and footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Push the app content up to remove empty header space */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 0rem !important;
}

/* Add a subtle glow to the primary button */
button[kind="primary"] {
    box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.4);
    transition: all 0.3s ease;
}
button[kind="primary"]:hover {
    box-shadow: 0 6px 8px -1px rgba(14, 165, 233, 0.6);
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- ASSET LOADING (CACHED FOR SPEED) ---
@st.cache_resource
def load_ai_model():
    return tf.keras.models.load_model("dermascan_phase1_best.keras")

@st.cache_data
def load_metadata_mapping():
    train_df = pd.read_csv("train_bridged.csv")
    _, label_mapping = pd.factorize(train_df['diagnosis'])
    return train_df, label_mapping

# --- PREPROCESSING ROUTINES ---
def preprocess_image(image_file):
    img = Image.open(image_file).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    return np.expand_dims(img_array, axis=0)

def preprocess_tabular(age, sex, site, train_df):
    age_mean = train_df['age'].mean()
    age_std = train_df['age'].std()
    age_scaled = (float(age) - age_mean) / age_std if age_std != 0 else 0.0
    
    sex_binary = 1.0 if str(sex).lower() == 'female' else 0.0
    
    site_cols = [c for c in train_df.columns if c.startswith('site_')]
    site_dict = {col: 0.0 for col in site_cols}
    target_col = f"site_{str(site).lower()}"
    if target_col in site_dict:
        site_dict[target_col] = 1.0
        
    feature_vector = [age_scaled, sex_binary] + [site_dict[col] for col in site_cols]
    return np.array([feature_vector], dtype=np.float32)

# --- BOOT SEQUENCE ---
try:
    model = load_ai_model()
    train_df, label_mapping = load_metadata_mapping()
except Exception as e:
    st.error(f"System Error (Missing Assets): {e}")
    st.stop()

# --- UI LAYOUT: STRUCTURAL UPGRADE ---
st.title("🔬 DermaScan AI")
st.markdown("### Multi-Modal Clinical Diagnostic Suite")
st.caption("Academic Prototype | Not for formal medical diagnosis.")

col1, col_space, col2 = st.columns([1, 0.1, 1.5])

with col1:
    st.subheader("1. Patient Intake")
    
    # Using a container card for a cleaner clinical grouping
    with st.container(border=True):
        uploaded_file = st.file_uploader("Upload Dermoscopic Image (.jpg, .png)", type=["jpg", "jpeg", "png"])
        
        st.markdown("##### Biological Metadata")
        
        # Upgraded slider to precision numeric input
        age = st.number_input("Patient Age", min_value=0, max_value=120, value=30, step=1)
        
        # Side-by-side dropdowns to save vertical space
        drop_col1, drop_col2 = st.columns(2)
        with drop_col1:
            sex = st.selectbox("Patient Sex", ["Male", "Female"])
        with drop_col2:
            site_cols = [c.replace('site_', '') for c in train_df.columns if c.startswith('site_')]
            site = st.selectbox("Anatomical Site", [s.title() for s in site_cols])
        
        st.divider()
        analyze_button = st.button("Generate Clinical Report", type="primary", use_container_width=True)

with col2:
    st.subheader("2. Diagnostic Intelligence")
    
    if uploaded_file is not None:
        if analyze_button:
            with st.spinner("Analyzing visual and biological markers..."):
                vision_tensor = preprocess_image(uploaded_file)
                tabular_tensor = preprocess_tabular(age, sex, site.lower(), train_df)
                
                predictions = model.predict({"vision_input": vision_tensor, "tabular_input": tabular_tensor}, verbose=0)[0]
                
                results = pd.DataFrame({
                    'Diagnosis': label_mapping,
                    'Probability': predictions
                }).sort_values(by='Probability', ascending=False).reset_index(drop=True)
                
                top_diagnosis = results.iloc[0]['Diagnosis']
                top_prob = results.iloc[0]['Probability']
                
                # Clinical Alert Card
                if "Melanoma" in top_diagnosis or "Carcinoma" in top_diagnosis:
                    st.error(f"### 🚨 High Risk: {top_diagnosis}\n**Confidence:** {top_prob:.1%}")
                else:
                    st.success(f"### 🟢 Benign Profile: {top_diagnosis}\n**Confidence:** {top_prob:.1%}")
                
                st.divider()
                
                # Upgraded visual spread (Replacing the chunky bar chart with clean progress metrics)
                st.markdown("##### Top Differential Diagnoses")
                for index, row in results.head(4).iterrows():
                    diag_name = row['Diagnosis']
                    prob_val = row['Probability']
                    st.markdown(f"**{diag_name}** - {prob_val:.1%}")
                    st.progress(float(prob_val))
                    
        else:
            st.image(uploaded_file, caption="Input Lesion Ready for Analysis", width=350)
    else:
        st.info("Awaiting patient intake. Please upload an image to begin.")
