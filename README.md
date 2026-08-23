# THIRDEYE V2 — AI-BASED FORENSIC FACE SKETCH AND RECOGNITION SYSTEM

[![Build Status](https://img.shields.io/badge/JavaFX-21.0.1-blue.svg)](https://openjfx.io/)
[![Python Service](https://img.shields.io/badge/FastAPI-0.141.1-green.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21.0-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Academic Final-Year Engineering Project**  
**System Code Name**: `ThirdEye v2`  
**Repository**: [github.com/mallikarjun086/third-eye](https://github.com/mallikarjun086/third-eye.git)  

---

## 1. PROJECT OVERVIEW

**ThirdEye v2** is an AI-assisted forensic workstation that enables law enforcement officers to interactively assemble composite facial sketches from eyewitness memory and automatically search those sketches against photographic suspect mugshot databases.

To bridge the severe **cross-modal domain gap** between sparse black-and-white line sketches and dense RGB photos, `ThirdEye v2` combines a **JavaFX Desktop Client** for sketch construction with a **Python/FastAPI Machine Learning Microservice** running a dual-stream feature extraction engine:

1. **Metric-Learned Deep Feature Stream**: A 512-dimensional FaceNet (`Inception-ResNet-v1`) embedding projected through a custom 2-layer MLP Projection Head (164,736 parameters) trained via Triplet Margin Loss ($\text{margin}=0.3$).
2. **Spatial Shape Feature Stream**: Contrast Limited Adaptive Histogram Equalization (CLAHE, `clipLimit=2.0`), $3 \times 3$ Gaussian blur, and an elliptical face-mask weighted **Histograms of Oriented Gradients (HOG)** descriptor (3,600 dimensions).
3. **Late Score Fusion**: A weighted fusion engine ($\alpha^* = 0.05$) combining deep semantic embeddings with spatial shape descriptors.

---

## 2. CANONICAL SYSTEM BENCHMARKS

* **Primary Held-Out Benchmark (189 Candidate Gallery)**: **85.71% Rank-1 Accuracy** (18/21 test queries, AUC = **0.9898**).
* **Secondary Test-Pool Benchmark (109 Candidate Gallery)**: **90.48% Rank-1 Accuracy** (19/21 test queries, AUC = **0.9914**).
* **100-Pair Evaluation Subset**: **92.00% Rank-1 Accuracy** (92/100 queries matched).
* **Raw FaceNet Baseline (Full Dataset 190 Queries)**: **12.11% Rank-1 Accuracy** (23/190 queries matched across raw 512-d FaceNet embeddings without projection or HOG).
* **Warm Matching Latency**: **307.90 ms median** (328.64 ms mean across 30 benchmark runs).

---

## 3. WHAT THE SYSTEM DOES NOT DO

To maintain complete academic honesty and defensibility during viva examination:

* **No Generative AI Sketch Synthesis**: Composite sketches are assembled via manual element layer selection (hair, eyes, nose, mouth, chin); the system does NOT use text-to-image or photo-to-sketch generative AI models (e.g., GANs, StyleGAN, Stable Diffusion).
* **No Cloud Dependency**: `ThirdEye v2` operates 100% offline without external cloud APIs (e.g., AWS Rekognition).
* **No Automatic 3D Pose Correction**: Input sketches and photos require front-facing or moderately rotated ($\le 15^\circ$) facial alignment.

---

## 4. SYSTEM ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JavaFX Desktop Client                             │
│                  (ThirdEye v2 / JDK 17 / Maven / JavaFX 21)                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            │                                                     │
            ▼                                                     ▼
┌───────────────────────────────┐                     ┌───────────────────────┐
│     SQLite Local Databases    │                     │   HTTP REST Interface │
│   (suspects.db, login.sqlite) │                     │ (JDK 11+ HttpClient)  │
└───────────────────────────────┘                     └───────────┬───────────┘
                                                                  │
                                                                  │ HTTP POST /match
                                                                  ▼
                                                      ┌───────────────────────┐
                                                      │  Python ML Service    │
                                                      │   (FastAPI / Uvicorn) │
                                                      └───────────┬───────────┘
                                                                  │
                 ┌────────────────────────────────────────────────┴────────────────────────────────┐
                 │                                                                                 │
                 ▼                                                                                 ▼
┌─────────────────────────────────┐                                               ┌─────────────────────────────────┐
│   Deep Feature Extraction       │                                               │    Spatial HOG Descriptor       │
│  (keras_facenet / TensorFlow)   │                                               │         (OpenCV / cv2)          │
└────────────────┬────────────────┘                                               └────────────────┬────────────────┘
                 │                                                                                 │
                 ▼                                                                                 ▼
┌─────────────────────────────────┐                                               ┌─────────────────────────────────┐
│ Cross-Modal Projection Head     │                                               │  Weighted Elliptical Face Mask  │
│(best_cross_modal_model.weights) │                                               │     (CLAHE + Gaussian Blur)     │
└────────────────┬────────────────┘                                               └────────────────┬────────────────┘
                 │                                                                                 │
                 └───────────────────────────────┐               ┌─────────────────────────────────┘
                                                 ▼               ▼
                                      ┌─────────────────────────────────────┐
                                      │       Late Score Fusion Engine      │
                                      │   S = 0.05 * S_deep + 0.95 * S_hog  │
                                      └──────────────────┬──────────────────┘
                                                         │
                                                         ▼
                                      ┌─────────────────────────────────────┐
                                      │    Cosine Similarity & Ranking      │
                                      └─────────────────────────────────────┘
```

---

## 5. REPOSITORY STRUCTURE

```text
Third-Eye/
├── README.md                                    # Master System Overview & Guide
├── .gitignore                                   # Hardened Git Ignore Manifest
├── scripts/
│   └── check_documentation_consistency.py        # Automated Documentation Validator
├── PROJECT_DOCUMENTATION/                       # Living Documentation System
│   ├── 00_START_HERE.md                          # Quick Start & Entry Point
│   ├── 01_CANONICAL_PROJECT_FACTS.md             # Authoritative System Metrics
│   ├── 02_PROJECT_STATUS.md                      # Verification Status Summary
│   ├── 03_CHANGELOG.md                           # Audit & Remediation Log
│   ├── 04_REPOSITORY_MAP.md                      # Full Repository Map
│   ├── REPOSITORY_CLEANUP_INVENTORY.md           # Cleanup & Artifact Inventory
│   ├── CANONICAL_COMPONENT_ARCHITECTURE.md       # Mermaid Architecture Diagrams
│   ├── REPOSITORY_POLLUTION_AUDIT.md             # Binary & Space Audit Report
│   ├── REPOSITORY_CLEANUP_PLAN.md                # Remediation Action Matrix
│   ├── LEGACY_COMPONENT_DECISION.md              # ThirdEye_FaceMatch Archive Note
│   ├── ML_EXPERIMENT_LINEAGE.md                  # Research Experiment Lineage
│   ├── LARGE_FILE_POLICY.md                      # Large File Storage Guidelines
│   ├── GIT_HYGIENE_REPORT.md                     # Git Health Verification
│   ├── DOCUMENTATION_CONTRADICTION_AUDIT.md      # Contradiction Fix Log
│   ├── POST_CLEANUP_VERIFICATION_REPORT.md       # Post-Cleanup Verification Log
│   ├── CLAIM_EVIDENCE_MATRIX.md                  # 17-Point Claim Verification Matrix
│   ├── MAINTENANCE_PROTOCOL.md                   # Documentation Governance SOP
│   ├── CHANGE_IMPACT_MATRIX.md                   # Code-to-Doc Impact Matrix
│   ├── DOCUMENTATION_SYNC_REPORT.md              # Script Output Report
│   ├── SECURITY_MIGRATION_PLAN.md                # Password Security Migration Plan
│   ├── FINAL_REPOSITORY_AUDIT.md                 # Master Audit Report
│   ├── FINAL_PROJECT_REPORT.md                   # 11-Chapter Academic Thesis
│   ├── VIVA_DEFENSE_GUIDE.md                     # Viva Elevator Pitches & 50 Q&A
│   └── RESEARCH_READINESS_ANALYSIS.md            # Paper Publishability Assessment
├── Project Code (forensic face sketch)/
│   └── Project Code (forensic face sketch)/
│       ├── ThirdEye v2/                          # [PRIMARY PRODUCTION SYSTEM]
│       │   ├── pom.xml                           # Maven JavaFX Build Configuration
│       │   ├── suspects.db                       # SQLite Suspect Database
│       │   ├── login.sqlite                      # SQLite User Login Database
│       │   ├── src/thirdeye/v2/                  # JavaFX Source Code & Assets
│       │   └── ml_service/                       # Python ML Microservice
│       │       ├── app.py                        # FastAPI Server & Model Warmup
│       │       ├── requirements.txt              # Service Dependencies
│       │       ├── run_tests.py                  # Automated Test Suite (7/7 Pass)
│       │       ├── FINAL_CANONICAL_METRICS.json  # Authoritative Metric Manifest
│       │       ├── split_manifest.json           # Identity Split Definition (60/20/21)
│       │       └── experiments/                  # Empirical Research Experiments (exp01..exp08)
│       └── ThirdEye_FaceMatch/                   # [LEGACY PROTOTYPE - ARCHIVED]
└── Third-Eye-Final-Year-Project/                 # Presentation Media & Paper Assets
```

---

## 6. PREREQUISITES & QUICK START

### Prerequisites

* **Java**: JDK 17+ (Java 21 recommended)
* **Build Tool**: Apache Maven 3.8+
* **Python**: Python 3.9 – 3.13

---

### Step 1: Start the Python ML Service

```bash
# Navigate to the ML service directory
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (runs on http://127.0.0.1:8000)
python app.py
```

*Wait for log confirmation*: `INFO Model warmed up at startup.`

---

### Step 2: Launch the JavaFX Application

```bash
# Open a second terminal window and navigate to the Java project root
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2"

# Compile and launch JavaFX client
mvn clean javafx:run
```

---

### Step 3: Run Automated Test Suite

```bash
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"
python run_tests.py
```

*Expected Output*: `Ran 7 tests in 46.801s - OK`

---

## 7. KNOWN LIMITATIONS & SECURITY STATUS

1. **Authentication Storage**: Passwords in `login.sqlite` are stored in plain text (`WHERE email = ? AND password = ?` in `Login_screenController.java`). A 4-step bcrypt migration plan is documented in [`SECURITY_MIGRATION_PLAN.md`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/PROJECT_DOCUMENTATION/SECURITY_MIGRATION_PLAN.md).
2. **Local Coupling**: Client and server execute over local HTTP interface (`http://127.0.0.1:8000`).

---

## 8. LEGACY COMPONENT WARNING

The directory [`ThirdEye_FaceMatch`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye_FaceMatch) contains an early Java Swing prototype that used AWS Rekognition. **It is NOT part of the active production system** and is retained purely as historical engineering evidence. See [`LEGACY_COMPONENT_DECISION.md`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/PROJECT_DOCUMENTATION/LEGACY_COMPONENT_DECISION.md).
