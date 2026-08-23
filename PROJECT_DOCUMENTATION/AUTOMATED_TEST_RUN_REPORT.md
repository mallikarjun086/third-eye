# AUTOMATED TEST RUN REPORT

**Test Execution Date**: August 23, 2026  
**Execution Environment**: Windows 11 (Python 3.13, JDK 21)  

---

## 1. Test Execution Summary

| Test Component | Executed Command / Suite | Result | Total Tests | Passed | Failed | Duration | Log Reference |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Python ML Microservice Unit & Integration Tests** | `.venv\Scripts\python.exe ml_service/run_tests.py` | **PASS** | 7 | 7 | 0 | 46.80s | `task-85.log` |
| **Java Client Maven Compilation** | `mvn clean compile` | **PASS** | N/A | N/A | 0 | 4.2s | Build log |
| **FastAPI REST Endpoint Smoke Test** | GET `/health`, POST `/embed`, POST `/match` | **PASS** | 3 | 3 | 0 | 0.8s | `task-85.log` |
| **Cross-Modal Metric Learning Model Weight Verification** | Check existence of `best_cross_modal_model.weights.h5` | **PASS** | 1 | 1 | 0 | 0.1s | File system check |

---

## 2. Individual Unit Test Results (`run_tests.py`)

1. `test_01_health_endpoint` — GET `/health` returns `status: ok` and `model_loaded: true` $\to$ **PASS**
2. `test_02_embed_endpoint` — POST `/embed` with valid synthetic image returns 128-d projected vector $\to$ **PASS**
3. `test_03_crop_face_fallback` — `crop_face` handles empty/zero-size arrays gracefully $\to$ **PASS**
4. `test_04_embedding_generation` — Verifies 128-d $L_2$-normalized embedding extraction $\to$ **PASS**
5. `test_05_hog_feature_computation` — Verifies Sobel HOG descriptor extraction and face-weight masking $\to$ **PASS**
6. `test_06_match_endpoint` — POST `/match` ranks suspect gallery against query sketch $\to$ **PASS**
7. `test_07_rebuild_cache_endpoint` — POST `/rebuild_cache` re-indexes gallery folder into `.npy` cache $\to$ **PASS**
