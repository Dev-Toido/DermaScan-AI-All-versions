import os
import unittest
import numpy as np
from PIL import Image
import pandas as pd
import tempfile
import hashlib

from safety_net import validate_input, check_skin_lesion, apply_confidence_threshold, log_prediction

class TestSafetyNet(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validate_input_valid(self):
        img_path = os.path.join(self.temp_dir.name, "valid.jpg")
        img = Image.new('RGB', (224, 224), color = 'red')
        img.save(img_path, format='JPEG')
        
        self.assertTrue(validate_input(img_path))

    def test_validate_input_invalid_size(self):
        img_path = os.path.join(self.temp_dir.name, "small.jpg")
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(img_path, format='JPEG')
        
        self.assertFalse(validate_input(img_path))

    def test_validate_input_invalid_format(self):
        img_path = os.path.join(self.temp_dir.name, "invalid.bmp")
        img = Image.new('RGB', (250, 250), color = 'red')
        img.save(img_path, format='BMP')
        
        self.assertFalse(validate_input(img_path))

    def test_validate_input_missing_file(self):
        self.assertFalse(validate_input("nonexistent_file_path.jpg"))

    def test_check_skin_lesion_high_variance(self):
        # Create an image with high variance (random noise)
        np.random.seed(42)
        high_var_img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        self.assertTrue(check_skin_lesion(high_var_img))

    def test_check_skin_lesion_low_variance(self):
        # Create a blank wall image (low variance)
        low_var_img = np.full((224, 224, 3), 128, dtype=np.uint8)
        # add tiny noise
        np.random.seed(42)
        noise = np.random.randint(-2, 3, (224, 224, 3), dtype=np.int16)
        low_var_img = np.clip(low_var_img + noise, 0, 255).astype(np.uint8)
        
        self.assertFalse(check_skin_lesion(low_var_img))

    def test_apply_confidence_threshold_high(self):
        pred_dict = {
            'predicted_class': 'MEL',
            'confidence': 0.85,
            'risk_group': 'High Risk'
        }
        result = apply_confidence_threshold(pred_dict, threshold=0.6)
        self.assertEqual(result['predicted_class'], 'MEL')
        self.assertEqual(result['risk_group'], 'High Risk')

    def test_apply_confidence_threshold_low(self):
        pred_dict = {
            'predicted_class': 'MEL',
            'confidence': 0.45,
            'risk_group': 'High Risk'
        }
        result = apply_confidence_threshold(pred_dict, threshold=0.6)
        self.assertNotEqual(result['predicted_class'], 'MEL')
        self.assertEqual(result['risk_group'], 'Low Confidence')
        self.assertTrue('dermatologist' in result['recommendation'].lower())

    def test_log_prediction(self):
        log_file = os.path.join(self.temp_dir.name, "test_log.csv")
        image_hash = hashlib.sha256(b"fake_image_data").hexdigest()
        metadata = {'age': 45, 'sex': 'male', 'site': 'torso'}
        prediction = {'predicted_class': 'BKL', 'confidence': 0.92, 'risk_group': 'Low Risk'}
        
        # Test inserting first row
        df = log_prediction(None, image_hash, metadata, prediction, filepath=log_file)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['age'], 45)
        
        # Test appending second row
        prediction2 = {'predicted_class': 'MEL', 'confidence': 0.88, 'risk_group': 'High Risk'}
        df = log_prediction(df, image_hash, metadata, prediction2, filepath=log_file)
        self.assertEqual(len(df), 2)
        
        # Verify CSV is written correctly
        saved_df = pd.read_csv(log_file)
        self.assertEqual(len(saved_df), 2)
        self.assertEqual(saved_df.iloc[1]['predicted_class'], 'MEL')

if __name__ == '__main__':
    unittest.main()
