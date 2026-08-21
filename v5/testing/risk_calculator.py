import numpy as np

class RiskCalculator:
    """
    Converts the raw neural network probabilities from the Clinical DDx Head 
    and Etiology Head into an actionable Malignancy Risk Index (Low, Intermediate, High)
    for Dermatologists.
    """
    def __init__(self):
        # Define which classes in the 8-class DDx head are considered "Malignant"
        # Example mapping (will align with label_mapper.py):
        # 0: Melanoma (Malignant)
        # 1: Basal Cell Carcinoma (Malignant)
        # 2: Squamous Cell Carcinoma (Malignant)
        self.malignant_ddx_indices = [0, 1, 2]
        
        # Risk Thresholds
        self.high_risk_threshold = 0.65
        self.intermediate_risk_threshold = 0.35

    def calculate_risk(self, ddx_probs, etiology_probs):
        """
        Calculates the Malignancy Risk Index.
        
        Args:
            ddx_probs (list or np.array): Probabilities from the 8-class DDx head.
            etiology_probs (list or np.array): Probabilities from the 4-class Etiology head.
            
        Returns:
            dict: Contains the Risk Index, Risk Score, and Top 3 DDx.
        """
        ddx_probs = np.array(ddx_probs)
        
        # Sum the probabilities of all malignant classes
        malignancy_score = np.sum(ddx_probs[self.malignant_ddx_indices])
        
        # Determine the Risk Category
        if malignancy_score >= self.high_risk_threshold:
            risk_index = "HIGH RISK - Excisional Biopsy Recommended"
        elif malignancy_score >= self.intermediate_risk_threshold:
            risk_index = "INTERMEDIATE RISK - Close Clinical Monitoring or Biopsy"
        else:
            risk_index = "LOW RISK - Benign Morphology"
            
        # Extract Top 3 Differential Diagnoses (Indices)
        top_3_indices = np.argsort(ddx_probs)[::-1][:3]
        top_3_probs = ddx_probs[top_3_indices]
        
        return {
            "risk_index": risk_index,
            "malignancy_score": float(malignancy_score),
            "top_3_ddx_indices": top_3_indices.tolist(),
            "top_3_probabilities": top_3_probs.tolist()
        }

if __name__ == "__main__":
    # Mock Test
    calc = RiskCalculator()
    
    # Mock model output (High probability for class 0 - Melanoma)
    mock_ddx = [0.75, 0.05, 0.01, 0.04, 0.10, 0.02, 0.02, 0.01] 
    mock_etiology = [0.80, 0.10, 0.05, 0.05]
    
    result = calc.calculate_risk(mock_ddx, mock_etiology)
    print("Clinical Output:")
    print(f"- Risk: {result['risk_index']} (Score: {result['malignancy_score']:.2f})")
    print(f"- Top 3 Indices: {result['top_3_ddx_indices']}")
