# THIRDEYE V2 — AI-BASED FORENSIC FACE SKETCH AND RECOGNITION SYSTEM

[![JavaFX](https://img.shields.io/badge/JavaFX-21.0.1-blue.svg)](https://openjfx.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-green.svg)](https://fastapi.tiangolo.com/)
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
3. **Late Score Fusion**: A weighted fusion engine ($\alpha^* = 0.05$) combining deep semantic embeddings with spatial shape descriptors ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$).

---

## 2. CANONICAL SYSTEM BENCHMARKS

* **Primary Held-Out Benchmark (189 Candidate Gallery)**: **85.71% Rank-1 Accuracy** (18/21 test queries, AUC = **0.9898**).
* **Secondary Test-Pool Benchmark (109 Candidate Gallery)**: **90.48% Rank-1 Accuracy** (19/21 test queries, AUC = **0.9914**).
* **100-Pair Evaluation Subset**: **92.00% Rank-1 Accuracy** (92/100 queries matched).
* **Raw FaceNet Baseline (Full Dataset 190 Queries)**: **12.11% Rank-1 Accuracy** (23/190 queries matched across raw 512-d FaceNet embeddings without projection or HOG).
* **Warm Matching Latency**: **307.90 ms median** (328.64 ms mean across 30 benchmark runs).

---

## 3. LITERATURE REVIEW & GAP ANALYSIS

`ThirdEye v2` is benchmarked against 6 key peer-reviewed literature works in forensic facial sketch recognition:

| Referenced Research Paper | Primary Methodology | Literature Limitation | How ThirdEye v2 Outperforms |
| --- | --- | --- | --- |
| **CHEHRA** (Mohan et al., *IJARSCT*, 2022) | Drag-and-drop web UI + AWS Rekognition API | Cloud dependency; privacy risk for suspect data | **100% Offline & Air-Gapped** local execution |
| **RecogniPro** (Shaikh et al., *IJCRT*, 2024) | Web sketch creation + cloud deep learning | Cloud network latency; lacks spatial feature fusion | Dual-Stream Late Fusion ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$) |
| **X-Bridge** (Itole et al., *IJECE*, 2024) | GAN image-to-image photo synthesis | High compute; GAN hallucinations distort identity | Structural metric projection head (**Zero Hallucination**) |
| **GenAI Police Sketches** (Sádaba-Campo et al., *BDCC*, 2025) | Text-to-Image Diffusion (Stable Diffusion / ControlNet) | Non-reproducible; questionable court admissibility | **Deterministic component assembly (100% Court-Admissible)** |
| **Forensic Sketch** (Pushpalatha et al., *IJRASET*, 2025) | Layered assembly + basic CNN feature maps | Low cross-modal accuracy (high domain gap drop) | **85.71% Rank-1 Accuracy** vs. 12.11% raw CNN baseline |
| **AI-Driven Sketch** (Pasunuri et al., *ICCSCE*, 2025) | Element recommendations + visual feature highlights | Cloud dependency; unoptimized fusion weighting | Empirically optimized late fusion ($\alpha^* = 0.05$) |

*For full details, read [`PROJECT_DOCUMENTATION/RESEARCH_PAPER_GAP_ANALYSIS.md`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/PROJECT_DOCUMENTATION/RESEARCH_PAPER_GAP_ANALYSIS.md).*

---

## 4. WHAT THE SYSTEM DOES NOT DO

To maintain complete academic honesty and defensibility during viva examination:

* **No Generative AI Sketch Synthesis**: Composite sketches are assembled via manual element layer selection (hair, eyes, nose, mouth, chin); the system does NOT use text-to-image or photo-to-sketch generative AI models (e.g., GANs, StyleGAN, Stable Diffusion).
* **No Cloud Dependency**: `ThirdEye v2` operates 100% offline without external cloud APIs (e.g., AWS Rekognition).
* **No Automatic 3D Pose Correction**: Input sketches and photos require front-facing or moderately rotated ($\le 15^\circ$) facial alignment.

---

## 5. SYSTEM ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JavaFX Desktop Client                             │
│                  (ThirdEye v2 / JDK 21 / Maven / JavaFX 21)                 │
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

## 6. REPOSITORY STRUCTURE

```text
Third-Eye/
├── README.md                                    # Master System Overview & Guide
├── .gitignore                                   # Hardened Git Ignore Manifest
├── scripts/
│   └── check_documentation_consistency.py        # Automated Documentation Validator
├── PROJECT_DOCUMENTATION/                       # Curated Canonical Documentation
│   ├── 00_START_HERE.md                          # Quick Start & Entry Point
│   ├── 01_CANONICAL_PROJECT_FACTS.md             # Authoritative System Metrics
│   ├── 02_PROJECT_STATUS.md                      # Verification Status Summary
│   ├── 03_CHANGELOG.md                           # Audit & Remediation Log
│   ├── 04_REPOSITORY_MAP.md                      # Full Repository Map
│   ├── CANONICAL_COMPONENT_ARCHITECTURE.md       # Architecture & Flow Diagrams
│   ├── CLAIM_EVIDENCE_MATRIX.md                  # 17-Point Claim Verification Matrix
│   ├── ENVIRONMENT_REQUIREMENTS.md               # JDK 21, Python, Maven Setup
│   ├── FINAL_PROJECT_REPORT.md                   # 11-Chapter Academic Thesis
│   ├── PRESENTATION_DEMO_GUIDE.md                # Examiner Demonstration Guide
│   ├── RESEARCH_READINESS_ANALYSIS.md            # Conference Readiness Assessment
│   ├── RESEARCH_PAPER_GAP_ANALYSIS.md            # Literature Gap Analysis
│   ├── SECURITY_MIGRATION_PLAN.md                # Password Security Migration Plan
│   ├── VIVA_DEFENSE_GUIDE.md                     # Viva Elevator Pitches & 50 Q&A
│   └── RESEARCH_PAPERS/                          # Reference Vault for Literature Papers
│       ├── 01_CHEHRA_Mohan_2022.md
│       ├── 02_RecogniPro_Shaikh_2024.md
│       ├── 03_Heterogeneous_Sketch_Itole_2024.md
│       ├── 04_Generative_Neural_Networks_Sadaba_2025.md
│       ├── 05_Forensic_Face_Sketch_Pushpalatha_2025.md
│       └── 06_AI_Driven_Forensic_Sketch_Pasunuri_2025.md
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
│       │       └── split_manifest.json           # Identity Split Definition (60/20/21)
│       └── ThirdEye_FaceMatch/                   # [LEGACY PROTOTYPE - ARCHIVED]
└── Third-Eye-Final-Year-Project/                 # Presentation Media & Paper Assets
```

---

## 7. PREREQUISITES & QUICK START

### Prerequisites

* **Java**: JDK 17+ (JDK 21 recommended)
* **Build Tool**: Apache Maven 3.8+
* **Python**: Python 3.9 – 3.13

---

### Step 1: Start the Python ML Microservice

```powershell
# Navigate to the ML service directory
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"

# Activate Virtual Environment (if using .venv)
..\..\..\..\..\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Start FastAPI server (runs on http://127.0.0.1:8000)
python app.py
```

*Wait for log confirmation*: `INFO Model warmed up at startup.`

---

### Step 2: Launch the JavaFX Application

```powershell
# Open a second terminal window and navigate to the Java project root
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2"

# Compile and launch JavaFX client
mvn clean javafx:run
```

---

### Step 3: Run Automated Test Suite

```powershell
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"
python run_tests.py
```

*Expected Output*: `Ran 7 tests in 46.801s - OK`

---

## 8. KNOWN LIMITATIONS & SECURITY STATUS

1. **Authentication Hashing Migration**: Passwords in `login.sqlite` can be migrated using the BCrypt hashing strategy detailed in [`PROJECT_DOCUMENTATION/SECURITY_MIGRATION_PLAN.md`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/PROJECT_DOCUMENTATION/SECURITY_MIGRATION_PLAN.md).
2. **Local Interface Coupling**: Client and server execute over a secure local REST interface (`http://127.0.0.1:8000`).

---

## 9. LEGACY COMPONENT WARNING

The directory [`ThirdEye_FaceMatch`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye_FaceMatch) contains an early prototype. It is NOT part of the active production system and is retained purely for historical reference.
