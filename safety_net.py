import os
import logging
from PIL import Image
import numpy as np
from datetime import datetime, timezone
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_input(image_path: str) -> bool:
    """
    Checks if file exists, is JPEG/PNG, and dimensions >= 224x224.
    Returns True if valid, else False and logs the reason.
    """
    if not os.path.exists(image_path):
        logger.error(f"File not found: {image_path}")
        return False
        
    try:
        with Image.open(image_path) as img:
            format_valid = img.format in ['JPEG', 'PNG']
            if not format_valid:
                logger.error(f"Invalid image format: {img.format}. Expected JPEG or PNG.")
                return False
                
            width, height = img.size
            if width < 224 or height < 224:
                logger.error(f"Image dimensions too small: {width}x{height}. Expected at least 224x224.")
                return False
                
    except Exception as e:
        logger.error(f"Error opening image: {e}")
        return False
        
    return True

def check_skin_lesion(image_array: np.ndarray) -> bool:
    """
    Implement a lightweight heuristic: calculate the variance of pixel intensities in a small central crop. 
    If variance is very low (e.g., < 500), suspect a non-skin image (e.g., a blank wall). 
    This is a placeholder; document that a proper skin-vs-non-skin classifier should replace it.
    
    Returns True if it looks like a skin lesion, False otherwise.
    """
    # NOTE: This is a placeholder heuristic. 
    # A proper skin-vs-non-skin binary classifier should be trained and deployed to replace this heuristic.
    
    if len(image_array.shape) < 2:
        return False
        
    h, w = image_array.shape[:2]
    # small central crop (e.g., 50x50 center)
    crop_size = min(50, h, w)
    start_y = h // 2 - crop_size // 2
    start_x = w // 2 - crop_size // 2
    
    crop = image_array[start_y:start_y+crop_size, start_x:start_x+crop_size]
    
    variance = np.var(crop)
    if variance < 500:
        logger.warning(f"Low pixel variance ({variance:.2f}) in central crop. Suspected non-skin image.")
        return False
        
    return True

def apply_confidence_threshold(prediction_dict: dict, threshold: float = 0.6) -> dict:
    """
    Takes the output from clinical_mapper and overrides if confidence < threshold as per the mapper's logic.
    """
    confidence = prediction_dict.get('confidence', 0.0)
    
    if confidence < threshold:
        return {
            'predicted_class': 'Unknown',
            'predicted_class_name': 'Unknown',
            'confidence': confidence,
            'risk_level': 'Low Confidence',
            'risk_group': 'Low Confidence',
            'color': '#808080',
            'recommendation': 'The model is not confident enough to make a prediction. Please consult a dermatologist.'
        }
    return prediction_dict

def log_prediction(log_df, image_hash: str, metadata: dict, prediction: dict, filepath: str = "inference_log.csv"):
    """
    Appends a row to a CSV log with timestamp, SHA256 image hash, age, sex, site, predicted class, confidence, risk group.
    """
    row = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'image_hash': image_hash,
        'age': metadata.get('age', metadata.get('age_approx', np.nan)),
        'sex': metadata.get('sex', 'unknown'),
        'site': metadata.get('site', metadata.get('anatom_site_general', 'unknown')),
        'predicted_class': prediction.get('predicted_class', 'Unknown'),
        'confidence': prediction.get('confidence', 0.0),
        'risk_group': prediction.get('risk_group', prediction.get('risk_level', 'Unknown'))
    }
    
    new_row_df = pd.DataFrame([row])
    
    if log_df is not None and not isinstance(log_df, pd.DataFrame):
        # Allow passing None, but ensure if it's not None it's a dataframe (or handled)
        pass
        
    if log_df is not None and not log_df.empty:
        updated_df = pd.concat([log_df, new_row_df], ignore_index=True)
    else:
        updated_df = new_row_df
        
    # save to csv
    mode = 'a' if os.path.exists(filepath) else 'w'
    header = not os.path.exists(filepath)
    new_row_df.to_csv(filepath, mode=mode, header=header, index=False)
    
    return updated_df
