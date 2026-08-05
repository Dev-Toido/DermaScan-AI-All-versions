# Project Constitution: DermaScan AI V3

## 1. Mission & Scope
In many parts of the world, a severe shortage of dermatologists leads to delayed diagnosis of skin cancers. DermaScan AI V3 addresses this by providing an AI-powered clinical decision-support tool. It helps dermatologists and general practitioners rapidly and accurately triage skin lesions from dermoscopic images by combining visual patterns with patient metadata. Unlike earlier versions, V3 strongly emphasizes clinical interpretability, explainability (Grad-CAM), professional workflow integration, and robust safety features.

## 2. Target Users
- **Primary:** Dermatologists and clinicians in outpatient departments.
- **Secondary:** General practitioners in rural or under-served areas where a specialist is not immediately available.
- *Note:* This is explicitly not a consumer app; it is designed for medical professionals as a second opinion.

## 3. Data Description
We are utilizing the ISIC 2019 Challenge Dataset.
- **Images:** 25,331 training images in JPEG format, located in `data/ISIC_2019_Training_Input/`.
- **Classes (8 diagnostic categories):** 
  - MEL (Melanoma)
  - NV (Melanocytic nevus)
  - BCC (Basal cell carcinoma)
  - AK (Actinic keratosis)
  - BKL (Benign keratosis)
  - DF (Dermatofibroma)
  - VASC (Vascular lesion)
  - SCC (Squamous cell carcinoma)
- **Metadata:** `age_approx`, `anatom_site_general`, `sex`. 
Missing values:

sex and anatom_site_general: add an "unknown" category.

age_approx: fill with median, and introduce an additional binary feature age_missing (1 if originally missing, 0 otherwise).
This preserves all samples and allows the model to learn from the pattern of missingness.

## 4. Model Architecture
**Multi-modal architecture** fusing image features with patient metadata to mirror clinical decision-making.

- **Image Stream:** EfficientNetB4 (pre-trained on ImageNet, classifier head removed). Output from the global average pooling layer yields a 1792-D feature vector.
- **Metadata Stream:** Preprocessed metadata (age normalized, sex binary, site one-hot encoded) mapped to a 32-D embedding via a small dense layer.
- **Fusion:** Concatenation of the 1792-D and 32-D vectors -> Dense(256) -> Dropout -> Dense(8, softmax).
- **Explainability:** EfficientNet is fully compatible with Grad-CAM, allowing heatmap generation from the last convolutional layer.

**Diagram:**
```text
Image → EfficientNetB4 (up to global_pool) → 1792-D vector ─┐
                                                              ├─ Concatenate → Dense(256) → Dropout → Dense(8, softmax)
Metadata (age, sex, site) → preprocessing → Dense(32) ───────┘
```

## 5. Training Plan
- **Environment:** Local training on a laptop (Intel Core i5 13th Gen, NVIDIA RTX 4050 with 6GB VRAM) using WSL2 with full GPU passthrough.
- **Framework:** TensorFlow / Keras with mixed precision (`tf.keras.mixed_precision.set_global_policy('mixed_float16')`) enabled.
- **Time Constraints:** 8 to 12 hours (overnight run).
- **Optimization:** If needed to meet time/memory constraints, reduce image resolution slightly or downgrade to EfficientNetB3.

## 6. Inference Pipeline Design
- **Offline Capability:** The pipeline runs entirely locally without internet dependency.
- **Clinical Interpretability:** Raw 8-class predictions are mapped to dermatologist-friendly risk groups:
  - **Malignant** (Red)
  - **Other Benign** (Yellow)
  - **Benign Nevi** (Green)
- **Performance:** Inference must complete in ≤ 2 seconds per image on the local machine (including preprocessing, model pass, Grad-CAM, and UI rendering).

## 7. UI/UX Plan
- **Deployment:** Primarily a local offline Streamlit web app. A live cloud demo (Streamlit Cloud / Hugging Face Spaces) will mirror the exact same codebase for competition showcase.
- **Design:** Professional dark theme with custom CSS and Lottie animations. 
- **Layout:** 
  - Sidebar for metadata inputs and image upload.
  - Main panel showing the uploaded image alongside the Grad-CAM heatmap.
  - Differential diagnosis bar chart and the clinical interpretation block (risk level & recommendation).
- **Reporting:** One-click generation of a downloadable clinical report PDF containing the image, heatmap, probabilities, metadata, and disclaimer.

## 8. Safety & Ethics
- **Disclaimers:** Always-visible in-app banner and PDF report footer stating: *"ACADEMIC PROTOTYPE – Not for clinical use. This tool is designed to assist, not replace, a medical professional."*
- **Bias Handling:** Transparent documentation via `MODEL_CARD.md` acknowledging dataset bias towards lighter skin tones. Use of weighted sampling during training.
- **Safety Net:** If confidence is < 60% or non-skin is detected, display an "Uncertain – consult a specialist" warning instead of a diagnosis. No automated follow-ups.
- **Audit Trail:** Local logging (`inference_log.csv`) tracking timestamp, anonymized image hash, metadata, and predictions. No PII is logged. UI reminder to ensure patient consent is obtained.

## 9. Success Criteria & Fallback Plan
- **Quantitative Metrics:** 
  - Top-1 Accuracy: ≥ 85%
  - F1-score (macro): ≥ 0.80
  - Sensitivity for Malignant classes: ≥ 85%
  - Specificity for Malignant classes: ≥ 90%
- **Qualitative Metrics:** Functional Grad-CAM successfully validated by biotech team for highlighting relevant lesion areas.
- **Fallback Plan:** If the V3 model test accuracy falls below 80%, we will revert to the robust V2 model (~90% real-world accuracy) but wrap it in the new V3 UI, Grad-CAM, and clinical mapping pipelines.

