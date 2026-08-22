# DermaScan AI (V5) 🔬

> **An advanced, multi-modal AI diagnostic assistant designed to triage skin lesions and mitigate skin-tone bias in dermatological deployments.**

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-v5.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)

## 📖 Overview
DermaScan AI (V5) is our most robust clinical decision-support architecture to date. Moving past the legacy flat-classification of V3 and V4, V5 introduces a **Dual-Head Multi-modal Architecture**. By fusing high-resolution dermoscopic images with 14-dimensional patient metadata (Age, Sex, Site), V5 categorizes lesions into 4 core biological Etiology Families before outputting the final 10-class diagnostic prediction.

This structure acts as a "clinical safety net," utilizing **Focal Loss** to heavily penalize False Negatives for melanocytic and malignant lesions.

---

## 📊 Comprehensive Reporting & Clinical Metrics
DermaScan AI includes an exhaustive reporting pipeline. We have synthesized technical benchmarks, biological variance metrics, and clinical utility into a single master document.

👉 **[Read the Super Detailed Full Report Here](docs/Super_Detailed_Full_Report.md)**

---

## 🚀 Getting Started (The One-Click Pipeline)

This repository comes pre-packaged with a multi-agent orchestration script. You can run the entire model inference testing suite, trigger the reporting subagents, and compile the final Markdown reports with a single command.

### 1. Prerequisites & Cloning
You must have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.
```bash
git clone https://github.com/Dev-Toido/DermaScan-AI-All-versions.git
cd DermaScan-AI-All-versions
```

### 2. Dataset Setup
*Note: Due to size constraints, the raw image datasets are not hosted in this repository.*
1. Download the merged ISIC + DermaCon-IN datasets from [Insert Kaggle/Drive Link Here].
2. Extract the images into the `archive/` folder at the root directory.

### 3. Initialize the Environment
Create the Conda environment using our exact specifications:
```bash
conda env create -f environment.yml
conda activate dermascan
```

### 4. Run the Pipeline
We have provided a "one-click" script that acts as the entrypoint for all 4 reporting subagents.
```bash
chmod +x run_super_report.sh
./run_super_report.sh
```

**What this script does:**
1. Loads the test datasets and mounts the Dual-Head V5 models to your GPU.
2. Generates the `metrics.json` via the inference suite.
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
