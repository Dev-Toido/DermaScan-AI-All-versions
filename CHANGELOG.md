# Changelog

## [v4.0.0] - 2026-08-05
### Added
- **V4 Architecture (FastAPI + Next.js)**: Introduced a robust, scalable Next.js frontend with a FastAPI backend to serve the underlying Keras model.
- **Repository Segregation**: Reorganized the repository to clearly separate V2, V3, and V4 architectures into independent subdirectories.
- **Enhanced Documentation**: Overhauled the README.md and introduced a standard `CHANGELOG.md` and `MODEL_CARD.md` for better reproducibility and deployment transparency.
- **Comprehensive Testing Suite**: Hardened the V3 logic with unit tests and balanced evaluation tests to confirm precision on 400 sample images (67.75% accuracy).

### Changed
- All test scripts and utility files moved to dedicated `tests/` and `scripts/` directories inside the `v3/` module.
- Path variables standardized to support independent execution from root or module directories.

### Removed
- Legacy files such as `evaluate_model_a.py`, duplicated `website/` folders, and old CSV logs were removed to clean the workspace.
