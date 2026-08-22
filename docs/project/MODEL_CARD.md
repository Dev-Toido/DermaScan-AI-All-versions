# Model Card: DermaScan AI (v3_best)

## Model Details
- **Architecture**: EfficientNetB4 (pre-trained on ImageNet) fine-tuned for dermatoscopic image classification.
- **Inputs**: 
  - `Image Input`: 380x380 RGB image (0-255 scaling, no normalization).
  - `Metadata Input`: 10-element vector (Age, Sex, 8-One-Hot Site encoding).
- **Outputs**: Probabilities for 8 ISIC skin lesion classes (NV, MEL, BKL, DF, SCC, BCC, VASC, AK).
- **Framework**: TensorFlow / Keras

## Intended Use
- **Primary Use Case**: Assisting researchers and educational symposiums in evaluating AI-driven dermatological classification.
- **Out-of-Scope Use Cases**: This model is **NOT** FDA-approved or certified for clinical diagnosis. Do not use for definitive patient care.

## Training Data
- Trained on the **ISIC 2019 dataset**, comprising over 25,000 dermatoscopic images. 
- A rigorous cleaning and balancing strategy was employed.

## Evaluation Results
- **Overall Accuracy**: 67.75% on a holdout balanced test set of 400 images (50 per class).
- **Class-level Sensitivity**:
  - Melanoma (MEL): 48.0%
  - Basal Cell Carcinoma (BCC): 60.0%
  - Squamous Cell Carcinoma (SCC): 56.0%
- *See `balanced_test/model_b_results.txt` for full classification report.*

## Ethical Considerations & Caveats
- **Skin Tone Bias**: The ISIC dataset predominantly features lighter skin tones, meaning the model may underperform on darker skin types.
- **Uncertainty**: A safety net mechanism warns users when the model's confidence is below 60%.
