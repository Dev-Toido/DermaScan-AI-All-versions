# Balanced Mini-Test Set Evaluation

This directory contains a portable, balanced mini-test set (400 images total, 50 per class) derived from the ISIC 2019 dataset.

## Instructions for Evaluating Model B

1. **Copy this folder**: Copy the entire `balanced_test/` folder to your project directory or machine.
2. **Environment**: Ensure you have a working Python environment with `tensorflow`, `pandas`, `numpy`, and `scikit-learn` installed.
3. **Configure the script**: Open `evaluate_model.py` and modify the `MODEL_OUTPUT_ORDER` dictionary at the top if your model outputs the 8 ISIC classes in an order different from the standard one. The default is `0: MEL, 1: NV, 2: BCC, 3: AK, 4: BKL, 5: DF, 6: VASC, 7: SCC`.
4. **Run the script**: Use the provided generic script to evaluate your Keras model (`.keras` or `.h5`).

```bash
# Basic run:
python evaluate_model.py path/to/your_model.keras

# If your model expects image pixel values normalized to [0, 1] instead of [0, 255]:
python evaluate_model.py path/to/your_model.keras --normalize
```

5. **Review Results**: The script will output the accuracy, inference time, sensitivity for malignant classes, and a full classification report. It will save these results to `model_b_results.txt`.
6. **Send Results**: After generating `model_b_results.txt`, please send that file back to me so we can combine the reports into a final comparison.
