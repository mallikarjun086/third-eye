# THIRD-EYE — BENCHMARK & SYSTEM REPRODUCTION GUIDE

**System:** Third-Eye — Forensic Face Sketch Construction & Recognition System  
**Document Purpose:** Independent Step-by-Step Reproduction Guide  

---

## 1. Prerequisites & Environment Setup

- **Python Version:** Python 3.10, 3.11, or 3.13
- **Dependencies:** Install required Python packages:
  ```bash
  pip install -r ml_service/requirements.txt
  ```
- **Pretrained FaceNet Weights:** Ensure `20180402-114759-weights.h5` exists in `C:\Users\<User>\.keras-facenet\20180402-114759\`.

---

## 2. Model Checkpoint Verification

Verify the SHA-256 hash of the Cross-Modal Projection Head weights:

- **File Path:** `ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5`
- **Expected Size:** `685,752` bytes
- **Expected SHA-256 Hash:** `727ad1d6b05f65fefde6149a5e47e35d3d4a063876d0dfeb7178c8b9127b7e4f`

PowerShell verification command:
```powershell
Get-FileHash -Path "ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5" -Algorithm SHA256
```

---

## 3. Running Automated System & API Tests

Execute the 7-test automated unit and regression suite:

```bash
cd ml_service
python run_tests.py
```

Expected Output:
```text
Ran 7 tests in ~17.2s

OK
```

---

## 4. Reproducing the Canonical ML Benchmarks

Execute the evaluation pipeline script:

```bash
cd ml_service
python run_baseline_repro.py
```

Expected Performance Outputs:

1. **Primary Protocol (21 Test Queries vs FULL 189 Gallery)**:
   - **Baseline (Model A):** **71.43% Rank-1** ($15 / 21$)
   - **Optimized (Model B):** **85.71% Rank-1** ($18 / 21$)
   - **Improvement:** **+14.28 percentage points**
2. **Secondary Protocol (21 Test Queries vs 109 Candidate Pool)**:
   - **Optimized (Model B):** **90.48% Rank-1** ($19 / 21$)
3. **Full Dataset Protocol (190 Queries vs 189 Gallery)**:
   - **Baseline (Model A):** **44.21% Rank-1** ($84 / 190$)
   - **Optimized (Model B):** **46.84% Rank-1** ($89 / 190$)

---

## 5. Launching the Production ML Service & Desktop UI

1. **Start ML Service:**
   ```bash
   cd ml_service
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
   ```
2. **Verify ML Health:** Open `http://127.0.0.1:8000/health` in your browser. Expected response:
   ```json
   {
     "status": "ok",
     "api_status": "UP",
     "model_loaded": true,
     "model_error": null
   }
   ```
3. **Launch Desktop UI:** Run the JavaFX application from NetBeans or Maven (`mvn javafx:run`).
