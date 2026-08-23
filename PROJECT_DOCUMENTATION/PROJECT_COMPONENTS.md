# PROJECT COMPONENTS & APPLICATIONS AUDIT

**Audit Date**: August 23, 2026  

---

## 1. Definitive Component Inventory

| Component ID | Path | Type | Entry Point | Build Command | Run Command | Purpose | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COMP-01** | `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2` | JavaFX App | `thirdeye.v2.ThirdEyeV2` | `mvn clean compile` | `mvn clean javafx:run` | Main Desktop Client UI for Sketch Construction & Match Submission | **PRIMARY PRODUCTION APPLICATION** |
| **COMP-02** | `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service` | Python FastAPI | `app.py` | `pip install -r requirements.txt` | `python app.py` / `uvicorn app:app --port 8000` | ML Matching & Feature Extraction Microservice | **PRODUCTION MICROSERVICE** |
| **COMP-03** | `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye_FaceMatch` | Java Swing | `com.mycompany.thirdeye_facematch.face_rekognition` | `mvn clean compile` | N/A (Cloud API Deprecated) | Early Java Swing Prototype using AWS Rekognition API | **LEGACY APPLICATION** |
| **COMP-04** | `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/experiments/exp05_cross_modal/cross_modal_trainer.py` | Python Script | `main()` | N/A | `python cross_modal_trainer.py` | Metric Learning Trainer for Keras Projection Head | **TRAINING PIPELINE** |
| **COMP-05** | `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/experiments/validation_audit/audit_pipeline.py` | Python Script | `main()` | N/A | `python audit_pipeline.py` | Empirical Benchmark & Latency Profiling Engine | **EVALUATION PIPELINE** |
| **COMP-06** | `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/run_tests.py` | Python Script | `unittest.main()` | N/A | `python run_tests.py` | Unit & API Integration Test Suite | **TEST SUITE** |

---

## 2. Definitive Answers to Component Totals

* **TOTAL REPOSITORY COMPONENTS**: 6
* **TOTAL ACTUAL APPLICATIONS**: 2 (`ThirdEye v2` Desktop + `ThirdEye_FaceMatch` Legacy)
* **TOTAL PRODUCTION COMPONENTS**: 2 (`ThirdEye v2` JavaFX Client + `ml_service` FastAPI Backend)
* **TOTAL EXPERIMENTAL COMPONENTS**: 1 (Experiments track `exp01` through `exp08`)
* **TOTAL TEST COMPONENTS**: 1 (`run_tests.py`)
* **TOTAL LEGACY COMPONENTS**: 1 (`ThirdEye_FaceMatch`)
* **TOTAL UTILITY COMPONENTS**: 1 (`prepare_dataset.py`, `precompute.py`, `cleardb.py`)
