# Model A Baseline Performance Report

## Dataset Description
- **Size**: 400 images total
- **Distribution**: 50 images per class (8 classes: MEL, NV, BCC, AK, BKL, DF, VASC, SCC)
- **Source**: Sampled from the ISIC 2019 test split, with deterministic random sampling for reproducibility. Classes with insufficient samples in the original test set were sampled with replacement to maintain exact balance.

## Performance Summary

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 67.75% |
| **Average Inference Time** | 0.1115 seconds/image |
| **Model Size** | ~78 MB |

### Sensitivity for Malignant Classes
- **MEL (Melanoma)**: 48.00%
- **BCC (Basal Cell Carcinoma)**: 60.00%
- **SCC (Squamous Cell Carcinoma)**: 56.00%

### Full Classification Report

| Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **MEL** | 0.62 | 0.48 | 0.54 | 50 |
| **NV** | 0.66 | 0.80 | 0.72 | 50 |
| **BCC** | 0.48 | 0.60 | 0.54 | 50 |
| **AK** | 0.58 | 0.70 | 0.64 | 50 |
| **BKL** | 0.69 | 0.44 | 0.54 | 50 |
| **DF** | 0.88 | 0.86 | 0.87 | 50 |
| **VASC** | 0.96 | 0.98 | 0.97 | 50 |
| **SCC** | 0.61 | 0.56 | 0.58 | 50 |

## Analysis

### Key Strengths
- **Benign Lesion Detection**: The model performs exceptionally well on distinct benign lesions, notably Vascular lesions (VASC) with 98% recall and Dermatofibroma (DF) with 86% recall.
- **Common Nevi**: The model correctly identifies 80% of common Nevi (NV), establishing a strong baseline for the most frequent clinical presentation.

### Weaknesses
- **Malignancy Sensitivity**: The model struggles to consistently detect malignant lesions, especially Melanoma (MEL) which only has 48% sensitivity. Basal Cell Carcinoma (BCC) and Squamous Cell Carcinoma (SCC) are better but still lack the high recall expected of a medical screening tool.
- **Benign Keratosis (BKL)**: The model misclassifies many BKL cases (44% recall), indicating it may confuse these with other visually similar lesions (like Melanoma or Nevi).
