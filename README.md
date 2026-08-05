# DermaScan AI V3

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Dev-Toido/DermaScan-AI-V3)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-14b8a6?logo=github)](https://Dev-Toido.github.io/DermaScan-AI-V3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DermaScan AI V3 is an advanced clinical decision support tool designed for the modern dermatologist. By fusing high-resolution dermoscopic imagery with biological metadata (age, sex, and anatomical site), DermaScan AI delivers a highly accurate, explainable, and safe prediction of skin lesion diagnosis.

## 🌟 Key Features

- **Multi-Modal Intelligence**: Combines visual features extracted via EfficientNetB4 with clinical metadata using a custom fusion network.
- **Explainable AI (XAI)**: Generates Grad-CAM heatmaps to visually explain which regions of the image the model focused on.
- **Clinical Safety Net**: Rejects low-confidence predictions (< 60%) to ensure it never "guesses" on challenging cases, strictly recommending professional consultation instead.
- **Clinical Risk Mapping**: Outputs actionable risk categories (Low, Medium, High) mapped to standard ISIC classes.
- **Offline & Private**: The entire application, including the UI and inference, runs locally, ensuring zero data leakage.

## 🚀 Live Demo

- **Marketing Website**: [Live Demo on GitHub Pages](https://Dev-Toido.github.io/DermaScan-AI-V3/)
- **Streamlit App**: Click the "Deploy to Streamlit" badge above to instantly deploy your own instance!

## ⚙️ Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Dev-Toido/DermaScan-AI-V3.git
   cd DermaScan-AI-V3
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```
4. **Run the Website Locally**:
   ```bash
   cd docs
   python -m http.server 8080
   # Open http://localhost:8080 in your browser
   ```

## 🧠 Model Architecture
DermaScan AI V3 utilizes an EfficientNetB4 vision backbone integrated with a metadata embedding pipeline. This architecture mirrors real clinical reasoning by contextualizing the image with patient data before the final dense layers make a prediction across 8 diagnostic categories.

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*Disclaimer: This is an academic prototype and is not intended for clinical use.*
