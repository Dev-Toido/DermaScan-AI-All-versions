# Model B Evaluation Report

## Model Details
- **File Path**: `models/dermascan_densenet_finetuned.pth`
- **File Size**: ~29.4 MB (30,829,564 bytes)
- **Architecture**: PyTorch-based DenseNet121

## Discovered Configuration
- **Image Size**: 380x380 (determined from `transforms.Resize((380, 380))` in `train_new_architecture.py`)
- **Normalization**: Standard ImageNet normalization (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
- **Multi-Modal**: No (Image-only model).
- **Class Order**: 7 classes. Maps model index output to ISIC abbreviations: 0: AK, 1: BCC, 2: BKL, 3: DF, 4: MEL, 5: NV, 6: VASC.
- **Notes**: The model was trained on 7 classes and does not predict SCC (Squamous Cell Carcinoma). As a result, its sensitivity for SCC is 0.

## Performance Metrics
- **Overall Accuracy**: 54.00%
- **Macro F1 Score**: 0.51
- **Weighted F1 Score**: 0.51

### Per-Class Performance
| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **MEL** (Melanoma) | 0.51 | 0.42 | 0.46 | 50 |
| **NV** (Melanocytic Nevi) | 0.61 | 0.72 | 0.66 | 50 |
| **BCC** (Basal Cell Carcinoma) | 0.47 | 0.58 | 0.52 | 50 |
| **AK** (Actinic Keratosis) | 0.31 | 0.56 | 0.40 | 50 |
| **BKL** (Benign Keratosis) | 0.53 | 0.54 | 0.53 | 50 |
| **DF** (Dermatofibroma) | 0.69 | 0.72 | 0.71 | 50 |
| **VASC** (Vascular Lesion) | 0.89 | 0.78 | 0.83 | 50 |
| **SCC** (Squamous Cell Carcinoma) | 0.00 | 0.00 | 0.00 | 50 |

### Sensitivity for Malignant Classes
- **MEL (Melanoma)**: 0.4200 (42.0%)
- **BCC (Basal Cell Carcinoma)**: 0.5800 (58.0%)
- **SCC (Squamous Cell Carcinoma)**: 0.0000 (0.0% - Model does not predict SCC)

## Inference Speed
- **Average Inference Time**: 0.1600 seconds/image (on CPU)

## Comparison Notes
*(Placeholder for comparing with Model A)*
- Note: This report is ready for a side-by-side comparison with the Model A evaluation report.
