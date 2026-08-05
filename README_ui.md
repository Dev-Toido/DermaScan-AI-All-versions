# DermaScan AI V3 - Streamlit UI

This is the front-end application for the DermaScan AI V3 Clinical Decision Support tool. It integrates the trained EfficientNetB4 multi-modal model with Grad-CAM visualization to provide an interpretable diagnostic tool for clinicians.

## Features

- **Professional Dark Theme**: Custom CSS applied for a modern and eye-friendly interface.
- **Safety Net**: Validates uploaded images (dimensions, format, skin lesion heuristic) and warns the user if confidence is low.
- **Grad-CAM Integration**: Automatically generates and overlays a gradient class activation heatmap to explain what visual features influenced the model's prediction.
- **Clinical Mapping**: Translates raw 8-class probabilities into actionable clinical recommendations (Malignant, Benign Nevi, Other Benign, Uncertain).
- **PDF Report Generation**: Users can generate and download a clinical summary PDF with the click of a button.

## Requirements

Ensure you have installed the requirements for the UI:
```bash
pip install streamlit pandas numpy opencv-python Pillow tensorflow fpdf streamlit-lottie requests scikit-learn
```

## Running the App

Execute the following command in the terminal:
```bash
streamlit run app_v3.py
```

## Important Files
- `app_v3.py`: Main Streamlit application file.
- `style.css`: Custom CSS styles injected into the app.
- `clinical_mapper.py`: Module responsible for mapping AI predictions to clinical risk groups.
- `safety_net.py`: Responsible for ensuring inputs are valid, safe, and logged.
- `gradcam.py`: Explains model predictions by generating spatial heatmaps.
- `preprocessing_objects.pkl`: Contains the trained `MinMaxScaler` and `OneHotEncoder` needed to preprocess the metadata for the model.
- `dermascan_v3_best.keras`: The trained multi-modal keras model (must be present in the directory).

## Disclaimer
As specified in the `Project_Constitution.md`, this is an **ACADEMIC PROTOTYPE** and not for clinical use without human oversight. The tool is designed to assist, not replace, a medical professional.
