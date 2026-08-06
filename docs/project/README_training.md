# Training DermaScan AI V3

This directory contains the training script (`train.py`) and model definition (`model.py`) for the DermaScan AI V3 multi-modal architecture.

## Dependencies

Before running the training script, ensure your environment has the required dependencies installed:

```bash
pip install tensorflow pandas numpy scikit-learn
```

Make sure that your hardware is properly configured for mixed precision if supported (the code sets `tf.keras.mixed_precision.set_global_policy('mixed_float16')`). This helps in reducing memory consumption and speeding up training, especially on modern GPUs (like NVIDIA RTX 4050).

## Prerequisites

You must run the data preprocessing script first to generate the necessary data splits (`train.csv`, `val.csv`, `test.csv`) and `preprocessing_objects.pkl`:

```bash
python preprocess.py
```

## Running the Training Script

To start the training process, simply run:

```bash
python train.py
```

### Optional Arguments
- `--data_dir`: Path to the data directory (default: `data`).
- `--epochs`: Number of epochs to train for (default: 50). Early stopping will likely end training sooner.
- `--batch_size`: Batch size (default: 8, which is safe for GPUs with 6GB VRAM).
- `--lr`: Initial learning rate (default: 1e-4).

Example with custom arguments:
```bash
python train.py --epochs 30 --batch_size 16 --lr 5e-5
```

## Outputs
- **`dermascan_v3_best.keras`**: The saved model weights for the epoch with the highest validation accuracy.
- **`training_log.csv`**: A CSV file containing the loss and metric progression across all epochs.
- **`test_evaluation.txt`**: After training is completed or stopped early, the model is evaluated on the test set. This text file contains the complete classification report and confusion matrix.
