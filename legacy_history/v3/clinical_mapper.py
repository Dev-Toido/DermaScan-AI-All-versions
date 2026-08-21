import json

# Order of classes based on ISIC_2019_Training_GroundTruth.csv
CLASS_NAMES = ["MEL", "NV", "BCC", "AK", "BKL", "DF", "VASC", "SCC"]

CLASS_FULL_NAMES = {
    "MEL": "Melanoma",
    "NV": "Melanocytic nevus",
    "BCC": "Basal cell carcinoma",
    "AK": "Actinic keratosis",
    "BKL": "Benign keratosis",
    "DF": "Dermatofibroma",
    "VASC": "Vascular lesion",
    "SCC": "Squamous cell carcinoma"
}

def map_prediction(class_abbr: str, confidence: float, demo_mode: bool = False) -> dict:
    """
    Maps a model prediction to a clinical message and risk group.
    
    Args:
        class_abbr: String abbreviation of the predicted class (e.g., 'MEL').
        confidence: Float representing the model's prediction confidence.
        
    Returns:
        A dictionary containing clinical mapping details.
    """
    if class_abbr not in CLASS_NAMES:
        class_name = "Unknown"
        class_full = "Unknown"
    else:
        class_name = class_abbr
        class_full = CLASS_FULL_NAMES.get(class_name, "Unknown")
        
    # Default values
    risk_group = "Unknown"
    risk_color = "grey"
    recommendation = "Consult a dermatologist."
    explanation = "No explanation available."
    
    if class_name in ["MEL", "BCC", "SCC"]:
        risk_group = "Malignant"
        risk_color = "red"
        recommendation = "Urgent biopsy suggested."
        explanation = f"The model detected visual patterns highly consistent with {class_full}, a form of skin cancer."
    elif class_name == "NV":
        risk_group = "Benign Nevi"
        risk_color = "green"
        recommendation = "Routine monitoring."
        explanation = f"The model detected features typical of a {class_full}, which is generally benign."
    elif class_name == "AK":
        risk_group = "Pre-Malignant"
        risk_color = "orange"
        recommendation = "Monitor closely or treat; possible biopsy if symptomatic."
        explanation = f"The model detected features consistent with {class_full}, which is a precancerous lesion that can evolve into skin cancer."
    elif class_name in ["BKL", "DF", "VASC"]:
        risk_group = "Other Benign"
        risk_color = "yellow"
        recommendation = "Monitor for changes; non-urgent evaluation."
        explanation = f"The model suggests {class_full}, which is typically benign but may warrant occasional monitoring."

    # Override for low confidence
    threshold = 0.5 if demo_mode else 0.6
    if confidence < threshold:
        risk_group = "Uncertain"
        risk_color = "grey"
        recommendation = "Insufficient confidence. Consult a dermatologist."
        explanation = "The model's confidence is too low to provide a definitive prediction. Clinical evaluation is strongly advised."
        
    return {
        "class_name": class_name,
        "class_full": class_full,
        "risk_group": risk_group,
        "risk_color": risk_color,
        "recommendation": recommendation,
        "explanation": explanation
    }

if __name__ == "__main__":
    # Generate full mapping in JSON format for the UI to load
    # We will generate mappings for each class with high confidence as the base mapping
    mapping_dict = {}
    for name in CLASS_NAMES:
        mapping_dict[name] = map_prediction(name, 0.99)
        
    mapping_json = json.dumps(mapping_dict, indent=4)
    print(mapping_json)
    
    with open("clinical_mapping.json", "w") as f:
        f.write(mapping_json)
