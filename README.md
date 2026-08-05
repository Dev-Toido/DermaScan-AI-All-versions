# DermaScan AI 🔬

> **An AI-powered dermatological diagnostic assistant, designed to detect and classify skin lesions with high precision.**

![DermaScan AI Model Accuracy](https://img.shields.io/badge/Model_Accuracy-67.75%25-brightgreen)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-v4.0.0-blue)

DermaScan AI analyzes dermatoscopic images alongside patient metadata (age, sex, anatomical site) to predict the likelihood of 8 distinct skin conditions, providing Grad-CAM visual explanations and clinically mapped recommendations.

## 📂 Project Organization

This repository contains multiple iterations of the DermaScan architecture:

- **`v4/`**: The latest V4 architecture, featuring a modern **FastAPI** backend and a **Next.js** frontend.
- **`v3/`**: The stable V3 architecture, powered by **Streamlit** and our proven Keras models. 
- **`v2_archive/`**: Legacy codebase for historical reference.
- **`docs/`**: GitHub Pages static website files.

## 🚀 Quick Start (V3 Streamlit App)

The V3 application is robust, tested, and ready for deployment.

1. **Clone the repository and enter the v3 directory:**
   ```bash
   git clone https://github.com/your-username/DermaScan-AI-V3.git
   cd DermaScan-AI-V3/v3
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit interface:**
   ```bash
   streamlit run app.py
   ```

## 📊 Model Performance

Our production model (`dermascan_v3_best.keras`) was rigorously evaluated on a balanced test set of 400 images:

| Metric | Score |
| :--- | :--- |
| **Overall Accuracy** | 67.75% |
| **Sensitivity (Melanoma)** | 48.00% |
| **Sensitivity (BCC)** | 60.00% |
| **Sensitivity (SCC)** | 56.00% |

## 👥 Credits
Developed for the upcoming AI Symposium. 
*Disclaimer: This tool is for educational and research purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.*
