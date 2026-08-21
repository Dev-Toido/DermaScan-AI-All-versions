# 🏎️ Epoch & GPU Optimization Plan

To train on your RTX 4050 efficiently and correctly, we need to restructure `train_loop.py` into a production-grade training pipeline and fix the CUDA/GPU bindings.

## 🚨 Open Questions for User
No questions right now, but please review the "What happens after" section below to understand the pipeline flow!

## 🛠️ Proposed Changes

### 1. Fix the GPU Binding (CUDA)
TensorFlow failed to detect your GPU because the base `tensorflow` package doesn't always bundle the NVIDIA drivers correctly for WSL.
- **Action:** I will update `requirements.txt` to use `tensorflow[and-cuda]==2.15.0`. This tells `pip` to automatically download the exact NVIDIA cuDNN and CUDA toolkit wheels required for your GPU.

### 2. Implement the "Best Approach" Epoch Strategy
Instead of a messy manual `for` loop, the best approach in TensorFlow is to **override the internal `train_step`** of the model so we can use Keras's built-in `model.fit()` while keeping Gradient Accumulation. This unlocks all the powerful Keras callbacks.

#### [NEW] `v5/training/custom_model.py`
- We will create a `DualHeadModel` class that inherits from `tf.keras.Model`.
- It will handle the Gradient Accumulation internally (waiting 4 steps before applying weights).

#### [MODIFY] `v5/training/train_loop.py`
We will implement the gold-standard Keras Callbacks for the `model.fit()` loop:
- **ModelCheckpoint:** Automatically saves the best model weights to `v5/training/checkpoints/best_model.h5` every time the validation loss improves.
- **EarlyStopping:** Stops training if the model stops improving for 5 epochs (prevents overfitting).
- **ReduceLROnPlateau:** Automatically lowers the learning rate if the model gets stuck.
- **TensorBoard:** Logs all metrics so you can visualize the training graph in your browser.

---

## 🔮 What Happens After the Epochs?

Once you run the command and the epochs finish (which could take 4-12 hours depending on the Early Stopping), here is exactly what happens next:

1. **The best weights are saved:** `best_model.h5` will be resting in your checkpoints folder.
2. **Phase 4 (Validation & Metrics):** We will load that `best_model.h5` and run it against the 15% unseen Test Set. We will generate Confusion Matrices, ROC curves, and calculate exactly how safe the Etiology Safety Net is.
3. **Phase 5 (FastAPI Integration):** We wrap the model in a Python FastAPI backend.
4. **Phase 6 (Next.js UI):** We build a beautiful web interface to upload images and see the dual-head predictions.

If you approve this plan, I will write the code, fix the GPU dependency, and hand you the final command to run in your terminal!
