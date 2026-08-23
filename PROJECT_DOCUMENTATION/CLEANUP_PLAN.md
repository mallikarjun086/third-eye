# REPOSITORY CLEANUP PLAN

**Plan Date**: August 23, 2026  

---

## 1. Targeted Non-Essential Build Artifacts

1. `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/target/` (Temporary Maven compiled output — generate on demand via `mvn clean compile`).
2. `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye_FaceMatch/target/` (Temporary Maven compiled output).
3. `ml_service/__pycache__/` & experiment `__pycache__/` folders (Python bytecode cache).

---

## 2. Protected Essential Research & Code Assets (DO NOT DELETE)

1. `ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5` (Trained Metric Learning Model Weights).
2. `ml_service/split_manifest.json` (Dataset Identity Splits).
3. `ml_service/FINAL_CANONICAL_METRICS.json` (Authoritative Benchmark Results).
4. `ml_service/experiments/experiment_registry.csv` (Experiment Track History).
5. `Third-Eye-Final-Year-Project/` (Project documentation PDFs, logo image, and published paper).
