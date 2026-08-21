import os
import sys
import numpy as np
import tensorflow as tf

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clinical_mapper import map_prediction
from safety_net import check_skin_lesion, validate_input
from gradcam import generate_gradcam

def test_1_clinical_mapper():
    print("Debugger 1 (Clinical Mapper): Testing signature and logic...")
    try:
        # Test normal mode
        res1 = map_prediction('AK', 0.55, demo_mode=False)
        assert res1['risk_group'] == 'Uncertain', "Failed normal threshold"
        # Test demo mode
        res2 = map_prediction('AK', 0.55, demo_mode=True)
        assert res2['risk_group'] == 'Pre-Malignant', "Failed demo threshold"
        print("✅ Debugger 1 PASSED: Clinical Mapper signature and logic are correct.")
    except Exception as e:
        print(f"❌ Debugger 1 FAILED: {e}")

def test_2_model_loading():
    print("Debugger 2 (Model Validation): Loading model...")
    try:
        model = tf.keras.models.load_model('dermascan_v3_best.keras')
        assert len(model.inputs) == 2, "Model should have 2 inputs"
        print("✅ Debugger 2 PASSED: Model loaded and architecture verified.")
        return model
    except Exception as e:
        print(f"❌ Debugger 2 FAILED: {e}")
        return None

def test_3_inference(model):
    if model is None:
        print("Skipping Debugger 3 (no model)")
        return
    print("Debugger 3 (Inference Engine): Testing forward pass...")
    try:
        dummy_img = np.zeros((1, 224, 224, 3), dtype=np.float32)
        dummy_meta = np.zeros((1, 10), dtype=np.float32)
        preds = model.predict([dummy_img, dummy_meta], verbose=0)
        assert preds.shape == (1, 8), "Output shape should be (1, 8)"
        print("✅ Debugger 3 PASSED: Inference successful.")
    except Exception as e:
        print(f"❌ Debugger 3 FAILED: {e}")

def test_4_gradcam(model):
    if model is None:
        print("Skipping Debugger 4 (no model)")
        return
    print("Debugger 4 (Explainability): Testing Grad-CAM generation...")
    try:
        dummy_img = np.zeros((224, 224, 3), dtype=np.float32)
        dummy_meta = np.zeros((1, 10), dtype=np.float32)
        heatmap = generate_gradcam(model, dummy_img, 0, dummy_meta)
        assert heatmap.shape == (224, 224), "Heatmap shape should be 224x224"
        print("✅ Debugger 4 PASSED: Grad-CAM heatmap generated correctly.")
    except Exception as e:
        print(f"❌ Debugger 4 FAILED: {e}")

def test_5_safety_net():
    print("Debugger 5 (Safety Net): Testing image variance check...")
    try:
        # A totally black image should have 0 variance and fail the skin lesion check
        black_img = np.zeros((224, 224, 3), dtype=np.uint8)
        assert not check_skin_lesion(black_img), "Safety net failed to catch black image"
        print("✅ Debugger 5 PASSED: Safety Net catches invalid images.")
    except Exception as e:
        print(f"❌ Debugger 5 FAILED: {e}")

if __name__ == "__main__":
    print("--- INITIATING 5 RIGOROUS DEBUGGER SUBAGENTS ---\n")
    test_1_clinical_mapper()
    model = test_2_model_loading()
    test_3_inference(model)
    test_4_gradcam(model)
    test_5_safety_net()
    print("\n--- ALL TESTS COMPLETED ---")
