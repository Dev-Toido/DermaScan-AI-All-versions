# 🩺 Clinical Dermoscopy Analysis System (DermaScan AI)

Welcome to the **DermaScan AI**! 🎉 This is an automated preliminary screening system designed to assist in dermatological diagnosis. This tool utilizes a fine-tuned Deep Learning model to analyze dermoscopic images and classify them into 9 distinct diagnostic categories.

## ✨ Premium UI/UX & Architecture
The platform recently underwent a massive visual and architectural overhaul to provide a **High-End SaaS** experience:
- **Modern Next.js Frontend:** Migrated from Gradio to a custom Next.js 15 application with Tailwind CSS and Framer Motion.
- **Glassmorphism & Gradients:** Sleek, modern visual hierarchy using dark-mode aesthetics.
- **Grad-CAM Integration:** Real-time AI attention heatmaps overlaid on lesion images.
- **Expanded Clinical Metadata:** Support for capturing anatomical sites (Ear, Foot, Genital, Hand, etc.) and patient demographics to pave the way for multimodal AI inference.

## 🧠 Core AI Engine
This system is powered by a PyTorch-based **DenseNet-121** neural network, trained on a massive dataset of over **26,000 augmented images** from the ISIC (International Skin Imaging Collaboration) archives. 📸

To prevent class imbalance (where common diseases overwhelm rare diseases), the model was trained using advanced **Anti-Lazy Class Weights**. This ensures our AI stays sharp and maintains high accuracy, even when identifying extremely rare conditions like Dermatofibromas.

### 🔬 Supported Diagnostic Categories
The model has been rigorously trained to output probabilities for the following 9 classes:
1. ☀️ Actinic Keratosis
2. 🔴 Basal Cell Carcinoma
3. 🤎 Benign Keratosis *(Includes Solar Lentigo & Seborrheic Keratosis)*
4. 🩹 Dermatofibroma
5. ⏺️ Melanocytic Nevi *(Common & Atypical Nevi)*
6. ⚠️ Melanoma
7. 🧓 Seborrheic Keratosis
8. 🩸 Vascular Lesion
9. 🦠 Warts-Molluscum

---

## 📁 Project Structure

```text
AIMED 2026/
│
├── frontend/                         # Next.js 15 + Tailwind CSS web application 🎨
├── data/                             # Raw datasets and test images 🗃️
├── models/                           # Trained PyTorch model weights (.pth files) 🧠
│   └── ultimate_dermascan_model.pth  # The primary 9-class model
│
├── Model.py                          # The Neural Network Architecture class 🏗️
├── app.py                            # FastAPI Backend server 🖥️
└── README.md                         # This documentation file 📖
```

---

## 🚀 Installation and Setup

The application is split into a **FastAPI backend** and a **Next.js frontend**. You will need two terminal windows to run it locally.

### 1️⃣ Backend Setup (FastAPI + PyTorch)
Make sure you have Python installed. You can install all required dependencies using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

Run the backend server (using Uvicorn for optimal performance):
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
*The API will start on `http://localhost:8000`.*

### 2️⃣ Frontend Setup (Next.js)
Open a new terminal window, navigate to the `frontend` directory, and install the Node modules:
```bash
cd frontend
npm install
npm run dev
```
*The web dashboard will start on `http://localhost:3000`.*

---

## 🖱️ How to Use
1. Open `http://localhost:3000` in your web browser.
2. Enter the clinical metadata (Lesion Location, Patient Sex).
3. **Upload** a high-quality dermoscopic image.
4. Click **Initialize Scan**.
5. The model will analyze the image, generate a Grad-CAM heatmap, and display the top diagnostic probabilities on the results dashboard.

---

## ⚖️ Disclaimer
> **FOR INVESTIGATIONAL USE ONLY.** 🏥
> This system provides automated analysis of dermoscopic images based on statistical modeling. It is designed to assist clinical research and must **not** be used as a substitute for professional medical judgment, histopathological evaluation, or formal clinical diagnosis.
