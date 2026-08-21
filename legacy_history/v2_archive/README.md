# 🔬 DermaScan AI: Multi-Modal Diagnostic Suite

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-FF6F00.svg?logo=tensorflow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B.svg?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> An advanced, multi-modal deep learning application that fuses dermoscopic vision data with patient biological metadata to generate probabilistic differential diagnoses for skin lesions.

---

## 📸 Interface Preview

<!-- REPLACE THIS LINK WITH YOUR ACTUAL SCREENSHOT URL -->
![DermaScan Clinical Dashboard](https://via.placeholder.com/1000x500.png?text=Upload+Your+Dashboard+Screenshot+Here)

*Figure 1: The clinical dashboard running local inference on an isolated test case.*

---

## 🚀 Live Demo & Presentation

<!-- REPLACE THIS LINK WITH YOUR STREAMLIT CLOUD URL -->
**Try the Application Here:** [Launch DermaScan AI Cloud App](https://your-streamlit-app-url-here.streamlit.app)

### 🎥 Video Walkthrough
<!-- REPLACE THIS LINK WITH YOUR YOUTUBE/DRIVE DEMO LINK -->
[![Watch the Demo](https://via.placeholder.com/600x300.png?text=Click+to+Watch+Video+Demo)](https://your-video-link-here.com)

---

## 🧠 System Architecture

Unlike standard image-classification pipelines, DermaScan AI mimics clinical workflows by interpreting both visual and biological markers simultaneously. 

### Multi-Modal Fusion Engine
1. **Visual Stream (Image Processing):** Extracts spatial features, border irregularity, and color variegation from dermoscopic imagery (`224x224` resolution).
2. **Tabular Stream (Biological Metadata):** Processes one-hot encoded anatomical site locations, binary sex variables, and normalized patient age.
3. **Concatenation Layer:** Both data streams are mathematically fused within a dense neural network to adjust baseline visual predictions against biological risk factors.

### Tech Stack
* **Deep Learning Framework:** TensorFlow / Keras
* **Data Manipulation:** Pandas, NumPy
* **Frontend Web App:** Streamlit (with custom clinical CSS injection)
* **Dataset:** ISIC (International Skin Imaging Collaboration) Archive

---

## 💻 Local Installation & Usage

To run this application locally and leverage your machine's hardware for rapid inference (0.5s per image):

### 1. Clone the Repository
```bash
git clone [https://github.com/Dev-Toido/DermaScanAI.git](https://github.com/Dev-Toido/DermaScanAI.git)
cd DermaScanAI
```

### 2. Install Dependencies
Ensure you are running a virtual environment (`venv` or `conda`), then install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Launch the Local Server
```bash
streamlit run app.py
```
The application will boot and become accessible in your local browser at `http://localhost:8501`.

---

## 📂 Repository Structure

| File | Description |
| :--- | :--- |
| `app.py` | The main Streamlit web application and UI logic. |
| `dermascan_phase1_best.keras` | The pre-trained multi-modal TensorFlow weights (Phase 1). |
| `train_bridged.csv` | Dataset reference used for dynamic metadata normalization. |
| `requirements.txt` | Cloud and local Python dependency map. |
| `.streamlit/config.toml` | Custom theme configurations for the clinical UI. |

---

## ⚠️ Academic & Clinical Disclaimer

**DermaScan AI is strictly an engineering prototype and academic research tool.** 
It is not FDA-approved and must not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider or dermatologist with any questions regarding medical conditions.

---

**Developed by Vivek Garai**
