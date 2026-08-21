# DermaScan AI V5 - Execution Tasks

## Phase 1: Preparation & Skeleton
- `[x]` Set up `/v5/` directory structure
- `[x]` Create `requirements.txt` for V5
- `[x]` Implement Dual-Head Architecture (`v5/training/model.py`)
- `[x]` Implement Focal Loss (`v5/training/losses.py`)
- `[x]` Implement Malignancy Risk Calculator (`v5/testing/risk_calculator.py`)

## Phase 2: Data Manipulation (Awaiting Download)
- `[x]` Analyze dataset schemas (ISIC + Diverse dataset)
- `[x]` Standardize metadata fields across different datasets
- `[x]` Write `dataset_merger.py` to mix and merge datasets
- `[x]` Segregate data into 70% Train, 15% Val, 15% Test splits
- `[x]` Write `label_mapper.py` (Etiology family mapping)
- `[x]` Build memory-efficient Data Generators (`v5/training/dataset.py`)

## Phase 3: Training & Validation
- `[x]` Write gradient-accumulation training loop (`v5/training/train_loop.py`)
- `[ ]` Train the model
- `[ ]` Validate Top-3 Accuracy
- `[ ]` Generate Grad-CAM heatmaps

## Phase 4: Finalization
- `[ ]` Generate V5 Super Full Detailed Report
- `[ ]` Integrate outputs into FastAPI/Next.js UI
- `[ ]` Fix Security: Remove Global State in API (prevent PDF/HIPAA cross-contamination)
- `[ ]` Fix Performance: Run TensorFlow inferences in non-blocking ThreadPools
