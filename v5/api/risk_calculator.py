import numpy as np

# dataset.py mappings
# DDX: 0: MEL, 1: NV, 2: BCC, 3: AK, 4: BKL, 5: DF, 6: VASC, 7: SCC, 8: UNK, 9: Other
DDX_CLASSES = {
    0: "Melanoma (MEL)",
    1: "Melanocytic Nevus (NV)",
    2: "Basal Cell Carcinoma (BCC)",
    3: "Actinic Keratosis (AK)",
    4: "Benign Keratosis (BKL)",
    5: "Dermatofibroma (DF)",
    6: "Vascular Lesion (VASC)",
    7: "Squamous Cell Carcinoma (SCC)",
    8: "Unknown/Indeterminate",
    9: "Other"
}

# ETIOLOGY: 0: Melanocytic, 1: Keratinocytic, 2: Vascular, 3: Inflammatory/Other
ETIOLOGY_CLASSES = {
    0: "Melanocytic",
    1: "Keratinocytic",
    2: "Vascular",
    3: "Inflammatory / Other"
}

class RiskCalculator:
    """
    Converts raw probabilities from the Dual-Head V5 Model into Malignancy Risk and Top DDx.
    """
    def __init__(self):
        # Malignant DDx Indices (Melanoma, BCC, AK, SCC)
        self.malignant_ddx_indices = [0, 2, 3, 7]
        self.high_risk_threshold = 0.65
        self.intermediate_risk_threshold = 0.35

    def calculate_risk(self, ddx_probs, etiology_probs):
        ddx_probs = np.array(ddx_probs)
        etiology_probs = np.array(etiology_probs)
        
        # Calculate Malignancy Score
        malignancy_score = np.sum(ddx_probs[self.malignant_ddx_indices])
        
        if malignancy_score >= self.high_risk_threshold:
            risk_index = "HIGH RISK"
            risk_color = "red"
            recommendation = "Urgent Excisional Biopsy or Dermatologist Review Recommended"
        elif malignancy_score >= self.intermediate_risk_threshold:
            risk_index = "INTERMEDIATE RISK"
            risk_color = "yellow"
            recommendation = "Close Clinical Monitoring or Biopsy Recommended"
        else:
            risk_index = "LOW RISK"
            risk_color = "green"
            recommendation = "Benign Morphology. Routine Monitoring."
            
        # Top 3 Differential Diagnoses
        top_3_indices = np.argsort(ddx_probs)[::-1][:3]
        top_3 = [{"class": DDX_CLASSES[i], "probability": float(ddx_probs[i])} for i in top_3_indices]
        
        # All DDX Probabilities
        all_ddx = {DDX_CLASSES[i]: float(ddx_probs[i]) for i in range(len(DDX_CLASSES))}
        
        # Etiology Probabilities
        all_etiology = {ETIOLOGY_CLASSES[i]: float(etiology_probs[i]) for i in range(len(ETIOLOGY_CLASSES))}
        
        # Check Safety Net (if Unknown/Indeterminate is the top prediction)
        is_uncertain = bool(top_3_indices[0] == 8)
        if is_uncertain:
            risk_index = "UNCERTAIN"
            risk_color = "orange"
            recommendation = "Model is highly uncertain. Manual Clinical Review Mandatory."
            
        return {
            "risk_index": risk_index,
            "risk_color": risk_color,
            "malignancy_score": float(malignancy_score),
            "recommendation": recommendation,
            "top_3_ddx": top_3,
            "all_ddx": all_ddx,
            "all_etiology": all_etiology,
            "is_uncertain": is_uncertain,
            "top_diagnosis": top_3[0]["class"]
        }
