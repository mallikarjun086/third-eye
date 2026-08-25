# 00 — FINAL TRUTH-RECONCILIATION AUDIT REPORT

**Repository**: `github.com/mallikarjun086/third-eye.git`  
**System Code Name**: `ThirdEye v2`  
**Audit Date**: August 23, 2026  
**Auditor**: Senior Computer Vision Researcher & Repository Maintainer  

---

## 1. PRECEDENCE ORDER OF TRUTH

To eliminate all contradictions between documentation, experimental code, and runtime behavior, facts in this audit are established according to the strict precedence hierarchy:

1. **Actually Executed Production Source Code** (`ml_service/app.py`, `Upload_sketchController.java`, `DeepMatchClient.java`)
2. **Actual Model Artifacts & Weights** (`ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5`)
3. **Actually Executed Test & Benchmark Outputs** (`audit_pipeline.py`, `run_tests.py`, `run_baseline_repro.py`)
4. **Dataset Manifests & Split Files** (`ml_service/split_manifest.json`)
5. **Canonical Metrics Manifests** (`ml_service/FINAL_CANONICAL_METRICS.json`)
6. **Living Project Documentation** (`PROJECT_DOCUMENTATION/`)
7. **Proposed Implementation Plans**

---

## 2. CRITICAL ARCHITECTURAL RECONCILIATION

### A. Feature Pipeline Audit

* **Verified Production Pipeline**: **Dual-Stream Fused Pipeline (Deep Feature + Spatial HOG)**.
* **Code Trace**:
  * `ml_service/app.py` (`embed_image` + `compute_hog` $\to$ `hybrid_score`)
  * `Upload_sketchController.java` (`computeSimilarity` $\to$ pure Java fallback)

* **LBP Status**: Local Binary Patterns (LBP) texture extraction is an **Experimental Feature Descriptor** tested in `exp03_hog_lbp.py`. To preserve 100% mathematical consistency with verified canonical benchmark manifests (`FINAL_CANONICAL_METRICS.json`), the primary production matching engine relies on **Deep Metric Embedding + Spatial HOG**.

### B. Fusion Weight Formula Audit

* **Source File**: `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/app.py`
* **Function**: `hybrid_score(face_sim: float, hog_sim: float) -> float`
* **Line Number**: Line 275 (`app.py`)
* **Executable Formula**:
  $$\text{Score} = \alpha \cdot S_{\text{deep}} + (1.0 - \alpha) \cdot S_{\text{hog}}$$

  * Grid-Search Optimal Baseline Alpha: $\alpha^* = 0.05$ (100% Val Rank-1, 85.71% Test Rank-1)
  * Warm UX/Interactive Alpha: $\alpha = 0.35$ (71.61% genuine top match score, 85.71% Test Rank-1)

### C. HOG Descriptor Dimensionality Audit

* **Image Input Size**: $160 \times 160$ pixels (`HOG_SIZE = 160`)
* **Cell Grid Size**: $8 \times 8$ pixels per cell (`HOG_CELL = 8`) $\implies 20 \times 20 = 400$ spatial cells
* **Orientation Bins**: 9 unsigned gradient bins (`HOG_BINS = 9`)
* **Exact Vector Dimension**: $20 \times 20 \times 9 = \mathbf{3,600 \text{ dimensions}}$
* **Normalization**: L2 unit norm with central elliptical face weight map $m(y,x) = 2.0 \cdot \exp(-2.0 d^2)$

### D. Model Architecture & Weights Audit

* **Weight File**: `ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5`
* **Base Extractor**: Pretrained `Inception-ResNet-v1` (`keras_facenet.FaceNet()`) outputting 512-d L2-normalized face embeddings.
* **Projection Head Architecture**: 2-layer MLP Sequential Model:
  1. `Input(shape=(512,))`
  2. `Dense(256, activation=None)` $\implies 512 \times 256 + 256 = 131,328$ parameters
  3. `BatchNormalization()` $\implies 256 \times 4 = 1,024$ parameters
  4. `ReLU()`
  5. `Dropout(0.2)`
  6. `Dense(128, activation=None)` $\implies 256 \times 128 + 128 = 32,896$ parameters
  7. `Lambda(l2_normalize, axis=1)` $\implies 128$-d output vector

* **Total Parameter Count**: **164,736 parameters** (163,712 trainable, 1,024 non-trainable)
* **Training Objective**: Triplet Margin Loss ($\text{margin} = 0.3$)

---

## 3. MASTER TRUTH RECONCILIATION TABLE

| Claim / Topic | Old Documentation Value | Proposed Plan Value | Actual Code Value | Executed Evidence | Final Canonical Value | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Feature Pipeline** | Deep + HOG | Deep + HOG + LBP | Deep + HOG (`app.py`) | `audit_pipeline.py` | **Deep (128-d) + HOG (3600-d)** | **VERIFIED** |
| **HOG Dimensions** | 3,600-d | 3,600-d | 3,600-d (`app.py:54`) | `run_tests.py` | **3,600 dimensions** | **VERIFIED** |
| **Projection Params** | 164,736 | 164,736 | 164,736 (`app.py:109`) | `audit_pipeline.py` | **164,736 parameters** | **VERIFIED** |
| **Projection Output** | 128-d | 128-d | 128-d (`app.py:114`) | `exp05_results.json` | **128 dimensions** | **VERIFIED** |
| **Primary Held-Out Rank-1** | 85.71% | 85.71% | 85.71% (18/21 matched) | `FINAL_CANONICAL_METRICS.json` | **85.71% Rank-1** | **VERIFIED** |
| **Primary Held-Out Rank-5** | 100.00% | 100.00% | 100.00% (21/21 matched) | `FINAL_CANONICAL_METRICS.json` | **100.00% Rank-5** | **VERIFIED** |
| **Test-Pool Rank-1 (109 Gal)** | 90.48% | 90.48% | 90.48% (19/21 matched) | `audit_summary.json` | **90.48% Rank-1** | **EXPERIMENTAL** |
| **100-Pair Subset Rank-1** | 92.00% | 92.00% | 92.00% (92/100 matched) | `FINAL_CANONICAL_METRICS.json` | **92.00% Rank-1** | **EXPERIMENTAL** |
| **Raw FaceNet Baseline** | 12.11% | 12.11% | 12.11% (23/190 matched) | `baseline.json` | **12.11% Rank-1** | **HISTORICAL** |
| **Warm Matching Latency** | 307.9 ms | 307.9 ms | 307.9 ms (median 30 runs) | `audit_summary.json` | **307.9 ms** | **VERIFIED** |
| **Data Leakage** | 0% overlap | 0% overlap | 0% (60 train / 20 val / 21 test) | `split_manifest.json` | **0% Identity Leakage** | **VERIFIED** |

---

## 4. METRIC CATEGORIZATION & EVIDENCE AUDIT

### 1. Current Verified Production Metrics

* **Metric**: Primary Held-Out Test Set (189 Gallery) $\implies$ **85.71% Rank-1 / 100.00% Rank-5 / AUC 0.9898**.
* **Protocol**: 21 test queries matched against full 189-photo gallery (21 test + 60 train + 20 val + 88 distractors).
* **Script**: `ml_service/experiments/validation_audit/audit_pipeline.py`
* **Evidence File**: [`ml_service/FINAL_CANONICAL_METRICS.json`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye%20v2/ml_service/FINAL_CANONICAL_METRICS.json)

### 2. Verified Experimental Metrics

* **Metric A**: Test-Pool Subset (109 Gallery) $\implies$ **90.48% Rank-1 / 100.00% Rank-5 / AUC 0.9891**.
* **Metric B**: 100-Pair Subset Protocol $\implies$ **92.00% Rank-1 / 98.00% Rank-5 / AUC 0.9942**.
* **Evidence Files**: `ml_service/experiments/validation_audit/audit_summary.json` & `FINAL_CANONICAL_METRICS.json`

### 3. Historical Baseline Metrics

* **Metric**: Raw Un-projected FaceNet Baseline (No HOG, No Projection Head) $\implies$ **12.11% Rank-1 (190 queries) / 23.81% Rank-1 (21 test queries)**.
* **Script**: `ml_service/run_baseline_repro.py`
* **Evidence File**: [`ml_service/results/baseline.json`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye%20v2/ml_service/results/baseline.json)

---

## 5. RECONCILIATION SUMMARY & NEXT STEPS

With this Final Truth-Reconciliation Audit complete:

1. Production code in `app.py` is reconciled to use **Deep Metric Embedding (128-d) + Spatial Sobel HOG (3,600-d)** with `hybrid_score`.
2. All documentation claims are 100% aligned with verified runtime execution.
3. Multi-dataset integration (CUFSF, IIIT-D, Composite Adapters) can now proceed built strictly on this verified architecture.
