# THIRDEYE V2 — QUICK START & SYSTEM ENTRY POINT

**Project Title**: AI-Based Forensic Face Sketch and Recognition System  
**System Code Name**: `ThirdEye v2`  

---

## 1. Quick Start Commands

### Step 1: Start the Python ML Service

```bash

# Navigate to the ML service directory

cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"

# Start the FastAPI service (runs on http://127.0.0.1:8000)

python app.py
```

*Wait for log output*: `INFO Model warmed up at startup.`

---

### Step 2: Launch the JavaFX Desktop Client

```bash

# In a second terminal, navigate to the Java project root

cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2"

# Compile and launch JavaFX application

mvn clean javafx:run
```

---

### Step 3: Run Automated Test Suite

```bash

# Run unit & API integration test suite

cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"
python run_tests.py
```

*Expected Output*: `Ran 7 tests in 46.801s - OK`
