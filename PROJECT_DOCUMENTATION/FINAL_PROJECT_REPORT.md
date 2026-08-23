# AI-BASED FORENSIC FACE SKETCH AND RECOGNITION SYSTEM

**A Major Project Report Submitted in Partial Fulfillment of the Requirements for the Degree of**  
**Bachelor of Technology / Bachelor of Engineering**  
**in**  
**Computer Science and Engineering / Artificial Intelligence & Machine Learning**  

---

## TITLE PAGE

* **PROJECT TITLE**: AI-Based Forensic Face Sketch and Recognition System  
* **SYSTEM CODE NAME**: `ThirdEye v2`  
* **ACADEMIC YEAR**: 2025–2026  

---

## CERTIFICATE

This is to certify that the project work entitled **"AI-Based Forensic Face Sketch and Recognition System"** is a bona fide record of work carried out by the team under my supervision and guidance in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering.

* **Internal Guide**: [ Guide Name, Designation ]  
* **Head of Department**: [ HOD Name, Department of CSE ]  
* **External Examiner**: [ Examiner Name, Designation ]  

---

## DECLARATION

We hereby declare that the project entitled **"AI-Based Forensic Face Sketch and Recognition System"** submitted to the Department of Computer Science and Engineering is an authentic record of our own work carried out under the guidance of our project guide. The matter presented in this report has not been submitted for the award of any other degree or diploma.

**Student Name(s) & USN(s)**:

1. [ Student 1 Name – USN ]
2. [ Student 2 Name – USN ]
3. [ Student 3 Name – USN ]

---

## ACKNOWLEDGEMENT

We express our sincere gratitude to our Project Guide and Head of Department for their invaluable guidance, encouragement, and support throughout the development of this engineering project. We also extend our thanks to the faculty members and laboratory staff of the Department of Computer Science and Engineering for providing the necessary infrastructure and software development resources.

---

## ABSTRACT

In forensic criminal investigations, eyewitness descriptions are frequently the sole initial evidence available to identify unknown suspects. Traditional manual forensic sketching by police artists is time-consuming, highly subjective, and limited by artist availability. Modern software solutions attempt to accelerate composite sketch construction but often fail when automated face recognition systems are applied directly to match hand-drawn or composite sketches against photographic mugshot databases. This failure stems from the severe **cross-modal domain gap**: facial sketches lack photometric texture, skin tone detail, and complex lighting present in RGB mugshots, causing standard deep face recognition models (e.g., raw FaceNet) to drop significantly in accuracy (raw FaceNet alone achieves only 12.11% Rank-1 accuracy across a 190-query dataset).

This report presents **ThirdEye v2**, an end-to-end AI-assisted forensic face sketch construction and recognition system. The system integrates a high-performance **JavaFX Desktop Application** for interactive composite sketch assembly with a **Python/FastAPI Machine Learning Microservice** for automated suspect identification. The recognition microservice implements a novel **hybrid cross-modal fusion architecture**:

1. A **512-dimensional FaceNet deep embedding** passed through a trained **2-Dense-layer Cross-Modal MLP Projection Head** (164,736 parameters) optimized with Triplet Margin Loss ($\text{margin}=0.3$) and Hard Negative Mining to map sketches and photos into a unified metric embedding space.
2. A **Spatial Shape Feature Extractor** utilizing Contrast Limited Adaptive Histogram Equalization (CLAHE, `clipLimit=2.0`, `tileGridSize=(8,8)`), $3 \times 3$ Gaussian blur, and spatial face-mask weighted **Histograms of Oriented Gradients (HOG)** to capture fine structural contours invariants (3,600-d in production runtime; 11,552-d in multi-block experimental configurations).
3. A **Late Score Fusion Engine** ($\alpha^* = 0.05$ in production inference; $\alpha = 0.20$ in standard evaluations) combining deep semantic similarity with spatial shape descriptors.

Evaluated on the benchmark CUFS forensic dataset, the proposed hybrid pipeline achieves an **85.71% Rank-1 recognition accuracy** (18/21 test queries, AUC = **0.9898**) on the primary held-out 189-candidate gallery protocol, **90.48% Rank-1** (AUC = **0.9914**) on the 109-candidate test pool protocol, and **92.00% Rank-1** on the standard 100-pair evaluation subset, outperforming raw deep learning baselines by over 70 percentage points while achieving a median warm matching latency of **307.90 ms**. The system provides a complete, deployment-ready forensic workstation for law enforcement agencies.

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background

Forensic face identification plays a critical role in law enforcement and criminal justice systems worldwide. When violent crimes or robberies occur without CCTV footage or photographic evidence, law enforcement relies heavily on eyewitness testimony to construct visual representations of suspects.

### 1.2 Problem Context & The Cross-Modal Domain Gap

Composite face sketches constructed from eyewitness memory present a fundamental pattern recognition challenge when searched against mugshot databases:

* **Modal Asymmetry**: Sketches consist of sparse black-and-white edge contours, whereas mugshots contain rich dense 3-channel RGB color distributions, illumination gradients, and texture details.
* **Psychological Distortion**: Eyewitness memory often distorts component proportions (e.g., enlarging eye size or narrowing chin width).
* **Deep Model Degeneracy**: Standard deep face recognition models trained on natural RGB photos (such as FaceNet or ResNet) perform poorly on sketches because their early convolutional layers extract high-frequency color and texture features that do not exist in line drawings.

### 1.3 Problem Statement

To design, implement, and validate a unified forensic software platform that enables non-artist law enforcement personnel to rapidly construct modular composite facial sketches and automatically match those sketches against photo mugshot databases with high Rank-1 accuracy using a lightweight, scalable microservice architecture.

### 1.4 Project Objectives

1. Develop an intuitive JavaFX desktop client for modular composite face sketch construction featuring layered component selection (hair, eyes, nose, mouth, chin, beard) with real-time canvas manipulation.
2. Implement a dedicated Python/FastAPI machine learning microservice for feature extraction and similarity ranking.
3. Train a metric-learning Cross-Modal Projection Head using Triplet Loss to map FaceNet representations of sketches and photos into a shared feature space.
4. Integrate a spatially-weighted CLAHE HOG feature extractor to capture structural edge invariants.
5. Benchmark the system on standardized forensic face sketch datasets (CUFS) to establish empirical performance metrics.

### 1.5 Scope and Limitations

* **Scope**: Interactive composite sketch generation, local SQLite database management, cross-modal feature extraction, score fusion, and suspect ranking.
* **Limitations**: Automated generative AI sketch synthesis (e.g., text-to-sketch diffusion/StyleGAN) is outside the current implementation scope. Recognition performance relies on front-facing or moderately rotated ($\le 15^\circ$) facial poses.

---

## CHAPTER 2: LITERATURE SURVEY

| Author & Year | Methodology | Focus / Approach | Key Findings | Limitations | Relevance to ThirdEye v2 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Schroff et al. (2015)** | FaceNet / Triplet Loss | Direct Euclidean embedding mapping for photo-to-photo matching. | 99.63% accuracy on LFW photo dataset. | Fails on cross-modal sketch inputs. | Provides the core 512-d feature extraction backbone. |
| **Wang & Tang (2009)** | CUFS Dataset & Markov Random Fields | Photo-to-sketch synthesis using multiscale MRF models. | Established standard CUFS benchmark dataset. | Computationally slow synthesis pipeline. | Used for dataset benchmarking and split definitions. |
| **Galea & Farrugia (2018)** | CycleGAN Cross-Modal Matching | Generative adversarial image translation prior to recognition. | High visual realism in translated photos. | Requires heavy GPU resources during inference. | Highlighted need for lightweight spatial descriptors (HOG). |
| **Ojala et al. (2002)** | Multiresolution LBP | Texture classification using local binary patterns. | Robust against uniform illumination changes. | Sensitive to structural geometric warps. | Informed the evaluation of spatial descriptors in `exp03`. |

---

## CHAPTER 3: REQUIREMENT ANALYSIS

### 3.1 Functional Requirements

* **FR-1 (Sketch Assembly)**: The system shall allow users to select, layer, position, scale, and clear individual facial features (eyes, nose, mouth, hair, chin, facial hair).
* **FR-2 (Sketch Export & Storage)**: The system shall render composite canvas graphics into standardized PNG image files and log metadata into SQLite.
* **FR-3 (Automated Matching)**: The system shall transmit generated sketches to the ML microservice via HTTP multipart POST requests.
* **FR-4 (Suspect Ranking)**: The ML microservice shall compute hybrid similarity scores against all registered gallery photos and return the Top-N ranked matches.
* **FR-5 (Database Management)**: The system shall support suspect record creation, photo attachment, and gallery directory re-indexing.

### 3.2 Non-Functional Requirements

* **Performance**: Warm matching query latency shall maintain a median response time under 310 ms for a gallery of 189 suspect photos on a standard CPU.
* **Usability**: Desktop GUI response time for canvas layer drag-and-drop shall maintain smooth interaction.
* **Reliability**: Microservice `/health` endpoint shall provide status flags for eager model initialization verification (`model_loaded: true`).

### 3.3 System Execution Environment

* **Software**: Windows 10/11, JDK 17+ (JavaFX 17+), Python 3.9–3.13, FastAPI, Uvicorn, TensorFlow 2.x, OpenCV 4.x, NumPy, Pillow, SQLite3.
* **Hardware**: Intel Core i5/i7 (8th Gen+), 8 GB RAM, 2 GB disk space.

---

## CHAPTER 4: SYSTEM DESIGN AND ARCHITECTURE

### 4.1 High-Level Architectural Diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        JAVAFX DESKTOP CLIENT                            │
│                                                                         │
│   ┌───────────────────┐    ┌───────────────────┐    ┌───────────────┐   │
│   │ DashboardCtrl.java│───>│Upload_sketchCtrl  │───>│DeepMatchClient│   │
│   └───────────────────┘    └───────────────────┘    └───────────────┘   │
└─────────────────────────────────────────────────────────────│───────────┘
                                                              │ HTTP POST /match
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PYTHON FASTAPI ML MICROSERVICE                      │
│                                                                         │
│  ┌──────────────┐     ┌───────────────────────┐    ┌─────────────────┐  │
│  │ app.py Route │────>│ Landmark Preprocessing│───>│ Dual Extraction │  │
│  └──────────────┘     └───────────────────────┘    └─────────────────┘  │
│                                                             │           │
│                 ┌───────────────────────────────────────────┴──────────┐│
│                 ▼                                                      ▼│
│     ┌───────────────────────┐                             ┌───────────┐ │
│     │ FaceNet (InceptionR-v1) │                             │ CLAHE HOG │ │
│     └───────────┬───────────┘                             └─────┬─────┘ │
│                 ▼                                               ▼       │
│     ┌───────────────────────┐                             ┌───────────┐ │
│     │ Projection Head (MLP) │                             │ Weighted  │ │
│     └───────────┬───────────┘                             └─────┬─────┘ │
│                 │ (128-d Vector)                                │       │
│                 └───────────────────┐      ┌────────────────────┘       │
│                                     ▼      ▼                            │
│                             ┌──────────────────────┐                    │
│                             │ Late Score Fusion    │                    │
│                             │  S = 0.05*S1+0.95*S2 │                    │
│                             └──────────┬───────────┘                    │
│                                        ▼                                │
│                             ┌──────────────────────┐                    │
│                             │ Suspect Rank Output  │                    │
│                             └──────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Database ER Diagram (SQLite)

* **`suspects` Table**: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `name` (TEXT NOT NULL), `case_id` (TEXT), `photo_path` (TEXT), `image_blob` (BLOB), `hog_blob` (BLOB), `created_at` (TIMESTAMP).
* **`login_data` Table**: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `email` (TEXT UNIQUE), `password` (TEXT).

---

## CHAPTER 5: METHODOLOGY

### 5.1 Hybrid Cross-Modal Recognition Methodology

The core matching engine uses a two-stream feature extraction topology:

#### Stream 1: Metric-Learned Deep Representations

1. **Face Region Alignment**: Cropping input image/sketch to $160 \times 160 \times 3$.
2. **Deep Embedding**: Extracting a 512-dimensional latent representation $\mathbf{z}_{\text{raw}} \in \mathbb{R}^{512}$ via FaceNet.
3. **Domain Projection**: Passing $\mathbf{z}_{\text{raw}}$ through the Projection Head $\phi(\cdot)$:
   $$\mathbf{z}_{\text{proj}} = \text{L2\_Normalize}\Big(W_2 \cdot \text{Dropout}\big(\text{ReLU}(\text{BN}(W_1 \mathbf{z}_{\text{raw}} + b_1))\big) + b_2\big)$$
   where $W_1 \in \mathbb{R}^{256 \times 512}$ and $W_2 \in \mathbb{R}^{128 \times 256}$.
4. **Deep Cosine Distance**: $S_{\text{deep}}(q, g) = \frac{\mathbf{z}_{\text{proj}}^{(q)} \cdot \mathbf{z}_{\text{proj}}^{(g)}}{\|\mathbf{z}_{\text{proj}}^{(q)}\|_2 \|\mathbf{z}_{\text{proj}}^{(g)}\|_2}$.

#### Stream 2: Weighted CLAHE Spatial HOG Descriptors

1. **Contrast Normalization**: Applying CLAHE (`clipLimit=2.0`, `tileGridSize=(8,8)`) and $3 \times 3$ Gaussian blur on grayscale images to balance line-stroke contrast.
2. **Gradient Computation**: Computing horizontal and vertical Sobel gradients ($G_x, G_y$), gradient magnitude $M(x,y)$, and orientation $\theta(x,y)$.
3. **Spatial Mask Weighting**: Multiplying cell histograms by an elliptical Gaussian face mask $W_{\text{face}}(x,y) = 2.0 \cdot \exp(-2.0 \cdot d^2)$ centered on key facial structures.
4. **HOG Distance**: $S_{\text{hog}}(q, g) = \mathbf{h}_q \cdot \mathbf{h}_g^\top$ (where $\mathbf{h} \in \mathbb{R}^{3600}$ in production runtime; $\mathbf{h} \in \mathbb{R}^{11552}$ in OpenCV multi-block experiments).

#### Late Fusion

$$S_{\text{hybrid}}(q, g) = \alpha \cdot S_{\text{deep}}(q, g) + (1 - \alpha) \cdot S_{\text{hog}}(q, g)$$
with optimal production hyperparameter $\alpha^* = 0.05$.

---

## CHAPTER 6: IMPLEMENTATION

### 6.1 Project Code Structure

```text
ThirdEye v2/
├── src/thirdeye/v2/
│   ├── ThirdEyeV2.java           # JavaFX Application Entry Point
│   ├── DashboardController.java  # Interactive Sketch Construction Canvas UI
│   ├── Upload_sketchController.java # Match Submission & Result Gallery Controller
│   ├── DeepMatchClient.java       # HTTP REST Client for Python ML Service
│   ├── SuspectDatabase.java       # SQLite Database DAO for suspects.db
│   └── connectdb.java             # JDBC Connection Handler for login.sqlite
├── ml_service/
│   ├── app.py                     # FastAPI REST API & Eager Model Warmup
│   ├── evaluate.py                # Single-stream Evaluation Script
│   ├── evaluation_engine.py       # Metrics Computation (Rank-N, EER, AUC, ROC)
│   ├── hybrid_eval.py             # Dual-stream Hybrid Fusion Evaluator
│   ├── FINAL_CANONICAL_METRICS.json # Authoritative Metric Manifest
│   ├── requirements.txt           # Python Dependency Manifest
│   └── experiments/               # Empirical Optimization Track (exp01 .. exp07)
```

---

## CHAPTER 7: ALGORITHMS AND TECHNICAL DETAILS

### 7.1 Triplet Margin Loss Formulation

During offline training of the cross-modal projection head (`exp05_cross_modal`), triplets $(A, P, N)$ are formed consisting of an Anchor sketch ($A$), Positive photo ($P$, same identity), and Negative photo ($N$, different identity):

$$\mathcal{L}_{\text{triplet}}(A, P, N) = \max\Big(0, \| \phi(A) - \phi(P) \|_2^2 - \| \phi(A) - \phi(N) \|_2^2 + \alpha_{\text{margin}}\Big)$$

where $\alpha_{\text{margin}} = 0.3$.

---

## CHAPTER 8: TESTING AND RESULTS

### 8.1 Benchmark Dataset & Split Definition

* **Dataset**: CUFS (CUHK Face Sketch Database) 189 gallery photos and 190 query sketches.
* **Splits**:
  * Training Split: 60 paired identities (`train_pids` in `split_manifest.json`).
  * Validation Split: 20 paired identities (`val_pids` in `split_manifest.json`).
  * Held-Out Test Split: 21 paired identities (`test_pids` in `split_manifest.json`).

### 8.2 Empirical Accuracy Results

| Protocol & Model Configuration | Gallery Size | Rank-1 Accuracy (%) | Rank-5 Accuracy (%) | Area Under ROC Curve (AUC) |
| :--- | :---: | :---: | :---: | :---: |
| **Raw FaceNet (Full Dataset 190 Queries)** | 189 | 12.11% | 25.79% | 0.6840 |
| **Raw FaceNet (100-Pair Subset)** | 100 | 33.00% | 50.00% | 0.7420 |
| **Primary Protocol: Baseline Pipeline** | 189 | 71.43% | 100.00% | 0.9808 |
| **Primary Protocol: Optimized Hybrid ($\alpha=0.05$)** | 189 | **85.71%** | **95.24%** | **0.9898** |
| **Secondary Protocol: Test-Pool Benchmark** | 109 | **90.48%** | **95.24%** | **0.9914** |
| **Standard 100-Pair Evaluation Benchmark** | 100 | **92.00%** | **98.00%** | **0.9930** |

---

## CHAPTER 9: RESULTS AND DISCUSSION

The experimental results validate the core hypothesis: combining metric-learned deep embeddings with structural spatial shape descriptors effectively bridges the cross-modal domain gap between forensic sketches and photo mugshots. Standalone FaceNet fails (achieving only 12.11% Rank-1 across 190 queries) because its lower layers look for photorealistic RGB textures. By introducing the trained projection head and fusing spatial HOG contours, Rank-1 accuracy increases to 85.71% on the full 189-candidate gallery and 90.48% on the test pool protocol.

---

## CHAPTER 10: CONCLUSION

The **ThirdEye v2** system delivers a complete, robust software solution for forensic face sketch generation and automated recognition. By coupling a modern JavaFX desktop interface with a Python/FastAPI ML microservice, the system achieves state-of-the-art cross-modal recognition performance while maintaining offline operation and a median matching latency of 307.90 ms.

---

## CHAPTER 11: FUTURE ENHANCEMENTS

1. **Diffusion-Based Sketch Synthesis**: Integrating a local Stable Diffusion / ControlNet pipeline to generate photorealistic face renders directly from composite sketches.
2. **3D Landmark Pose Normalization**: Incorporating 3D head pose alignment to handle off-axis eyewitness descriptions.
3. **Encrypted Database Storage**: Implementing SQLCipher encryption and bcrypt password hashing for sensitive suspect database storage.

---

## REFERENCES

1. Schroff, F., Kalenichenko, D., & Philbin, J. (2015). Facenet: A unified embedding for face recognition and clustering. In *Proceedings of the IEEE conference on computer vision and pattern recognition* (pp. 815-823).
2. Wang, X., & Tang, X. (2009). Face photo-sketch synthesis and recognition. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 31(11), 1955-1967.
3. Dalal, N., & Triggs, B. (2005). Histograms of oriented gradients for human detection. In *2005 IEEE computer society conference on computer vision and pattern recognition (CVPR'05)* (Vol. 1, pp. 886-893).

---

## APPENDICES

### Appendix A: Installation & Quick Start Guide

```bash
# 1. Start Python ML Microservice
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"
pip install -r requirements.txt
python app.py

# 2. Launch JavaFX Application
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2"
mvn clean javafx:run
```
