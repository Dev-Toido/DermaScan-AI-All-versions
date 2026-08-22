import os

def update_readme():
    path = "README.md"
    
    new_readme = """# DermaScan AI (V5) 🔬

> **An advanced, multi-modal AI diagnostic assistant designed to triage skin lesions and mitigate skin-tone bias in dermatological deployments.**

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-v5.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)

## 📖 Overview
DermaScan AI (V5) is our most robust clinical decision-support architecture to date. Moving past the legacy flat-classification of V3 and V4, V5 introduces a **Dual-Head Multi-modal Architecture**. By fusing high-resolution dermoscopic images with 14-dimensional patient metadata (Age, Sex, Site), V5 categorizes lesions into 4 core biological Etiology Families before outputting the final 10-class diagnostic prediction.

This structure acts as a "clinical safety net," utilizing **Focal Loss** to heavily penalize False Negatives for melanocytic and malignant lesions.

### V5.1 Expansion: Continuous Learning Loop
DermaScan AI now features a production-grade active feedback loop. When a dermatologist clicks "Submit Correction" via the UI to correct an AI misdiagnosis, the image and metadata are securely vaulted into a `/hard_examples/` database. The TensorFlow data pipeline uses a `90/10` Replay Buffer to mathematically penalize and learn from these edge-cases dynamically during the next training run.

---

## 📊 Comprehensive Reporting & Clinical Metrics
DermaScan AI includes an exhaustive reporting pipeline. We have synthesized technical benchmarks, biological variance metrics, and clinical utility into a single master document.

👉 **[Read the Super Detailed Full Report Here](docs/Super_Detailed_Full_Report.md)**

---

## 🚀 Getting Started (Using the AI)

We have heavily optimized the user experience. **You do NOT need to download the massive 25GB image datasets just to use the web application.** The trained model weights are all that is required for inference.

### 1. Prerequisites & Cloning
You must have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.
```bash
git clone https://github.com/Dev-Toido/DermaScan-AI-All-versions.git
cd DermaScan-AI-All-versions
```

### 2. One-Click Initial Setup
Run this script **once** when you first clone the repository. It will automatically build the Conda environment and install the Next.js UI node dependencies.
```bash
chmod +x setup.sh
./setup.sh
```

### 3. One-Click Application Startup
Run this script whenever you want to boot up the web interface to use the AI. It concurrently starts the FastAPI backend (Port 8000) and the Next.js frontend (Port 3000), pre-warms the models, and binds them to a single terminal process.
```bash
chmod +x start.sh
./start.sh
```
*Access the Web UI at: [http://localhost:3000](http://localhost:3000)*

---

## 🧪 Developer Commands (Training & Evaluation)

If you are a researcher who wants to train the models from scratch or run the full diagnostic evaluation suite to generate new Markdown reports, you will need the raw datasets.

### 1. Dataset Setup
*Note: Due to size constraints, the raw image datasets are not hosted in this repository.*
1. Download the merged ISIC + DermaCon-IN datasets from [Insert Kaggle/Drive Link Here].
2. Extract the images into the `archive/` folder at the root directory.

### 2. Generate Super Report
To run the native evaluation suite over the 25GB dataset and generate new Markdown reports:
```bash
chmod +x run_super_report.sh
./run_super_report.sh
```
**What this script does:**
1. Loads the test datasets and mounts the Dual-Head V5 models to your GPU.
2. Evaluates the models to generate the 10x10 Confusion Matrix and Top-1/Top-3 Accuracies in `metrics.json`.
3. Deploys the Clinical and Literature Subagents to generate qualitative analysis.
4. Compiles the quantitative scores and qualitative research into the final `docs/Super_Detailed_Full_Report.md`.

---

## 📁 Repository Structure
- **`v5/`**: The bleeding-edge V5 architecture (Dual-Head Models, Multi-modal TF Datasets, Focal Loss training loops).
- **`v5/reporting_agents/`**: Python subagents dedicated to analyzing and generating documentation.
- **`docs/`**: Generated reports, model cards, and the Super Detailed Report.
- **`v4/` & `v3/`**: Legacy architectures for historical reference.

## ⚠️ Disclaimer
**ACADEMIC PROTOTYPE – Not for clinical use.** This tool is designed to assist, not replace, a medical professional. It is not FDA-approved or certified for definitive clinical diagnosis.
"""
    with open(path, "w") as f:
        f.write(new_readme)
        
    print("README updated successfully!")

if __name__ == "__main__":
    update_readme()
