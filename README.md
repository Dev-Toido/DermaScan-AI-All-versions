# DermaScan AI 🔬

> **An AI-powered dermatological diagnostic assistant, designed to detect and classify skin lesions with high precision.**

![DermaScan AI Model Accuracy](https://img.shields.io/badge/Model_Accuracy-67.75%25-brightgreen)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-v4.0.0-blue)

## 📖 Overview
DermaScan AI is a clinical decision-support tool. It assists dermatologists and general practitioners in triaging skin lesions from dermoscopic images by combining visual patterns with patient metadata. DermaScan AI analyzes dermatoscopic images alongside patient metadata (age, sex, anatomical site) to predict the likelihood of 8 distinct skin conditions, providing Grad-CAM visual explanations and clinically mapped recommendations.

## 📂 Project Structure
This repository contains multiple iterations of the DermaScan architecture:
- **`v4/`**: The latest V4 architecture, featuring a modern **FastAPI** backend and a **Next.js** frontend. Highly scalable and decoupled.
- **`v3/`**: The stable V3 architecture, powered by **Streamlit** and our proven Keras models.
- **`v2_archive/`**: Legacy codebase for historical reference.
- **`docs/`**: Marketing website files, comprehensive project documentation, and reports.
- **`scripts/` & `tests/`**: Testing and utility scripts.

## 🧠 Model Architecture & Performance
- **Model**: Multi-modal EfficientNetB4 fusing image features with patient metadata (Age, Sex, 8-One-Hot Site encoding).
- **Outputs**: Probabilities for 8 ISIC skin lesion classes (NV, MEL, BKL, DF, SCC, BCC, VASC, AK).
- **Overall Accuracy**: 67.75% on a holdout balanced test set of 400 images.
- **Explainability**: Fully compatible with Grad-CAM to highlight the regions the model focuses on.
- *Note: Please see `docs/project/MODEL_CARD.md` for full model details, ethical considerations, and bias handling.*

## 🚀 Getting Started

### V4 (Latest Architecture: Next.js + FastAPI)
The V4 application is our modern web-stack version.
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dev-Toido/DermaScan-AI-V3.git
   cd DermaScan-AI-V3
   ```
2. **Run the V4 Launch Script:**
   ```bash
   chmod +x run_v4.sh
   ./run_v4.sh
   ```
   This script will start the FastAPI backend on `http://localhost:8000` and the Next.js frontend on `http://localhost:3000`.

### V3 (Streamlit App)
The V3 application is robust, tested, and ready for rapid local deployment.
1. **Navigate to the v3 directory:**
   ```bash
   cd v3
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Streamlit interface:**
   ```bash
   streamlit run app.py
   ```

## 🌐 Live Deployments
- **V4 App (Latest Architecture)**: [derma-scan-ai-all-versions.vercel.app](https://derma-scan-ai-all-versions.vercel.app/)
- **V3 Streamlit App**: [dermascan-ai-v3.streamlit.app](https://dermascan-ai-v3.streamlit.app/)
- **Marketing Website**: *(Deployment pending via GitHub Pages)*
- **V4 Backend API**: Hosted on Render

*(See `docs/project/DEPLOYMENT.md` for detailed instructions)*

## ⚠️ Disclaimer
**ACADEMIC PROTOTYPE – Not for clinical use.** This tool is designed to assist, not replace, a medical professional. It is not FDA-approved or certified for definitive clinical diagnosis.
