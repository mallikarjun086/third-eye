# FINAL ACCURACY IMPROVEMENT BASELINE AUDIT REPORT

**System Name**: ThirdEye v2 — AI-Based Forensic Face Sketch and Recognition System  
**Audit Timestamp**: August 24, 2026  
**Auditor**: Senior Computer Vision Researcher & Lead Systems Engineer  
**Repository**: `https://github.com/mallikarjun086/third-eye.git`  

---

## 1. EXECUTIVE SUMMARY & REPRODUCIBILITY AUDIT

A thorough, empirical audit was conducted on the live ThirdEye v2 matching engine to investigate the low matching scores (~47% Rank #1) observed during non-artist composite sketch demonstrations.

### Key Finding & Root Cause Analysis

The low match score (~41%–47%) and impostor misranking during composite sketch searches are **NOT** caused by model weight corruption or dataset missingness. The root cause is a **modality domain mismatch in spatial feature weighting**:

1. **HOG Spatial Gradient Mismatch**: The Spatial HOG feature stream ($3,600\text{-d}$) computes pixel-level gradient orientation histograms. While HOG performs well on artist-shaded pencil sketches ($78\%\text{--}85\%$ correlation), it exhibits high domain noise ($24.61\%$ correlation) when comparing vector composite sketches (clean black strokes on white canvas) against color photographs.
2. **Heavy HOG Weighting Penalty**: When `FACE_WEIGHT` is set to `0.35` (or `0.05`), the fusion formula forces $65\%\text{--}95\%$ of the match score onto HOG. This severely penalizes the true suspect (`a-sharukh.jpg`), dropping the true match score from **71.77%** (Deep Stream) to **41.12%** (Fused), allowing an impostor's background HOG correlation ($46.00\%$) to take Rank #1.
3. **Deep Metric Stream Precision**: The Cross-Modal FaceNet Projection Head (`best_cross_modal_model.weights.h5`) correctly projects composite face embeddings, achieving **71.77%** genuine similarity for the true target.
4. **Resolution**: Adjusting `FACE_WEIGHT` to `0.85` (85% Deep Metric Embedding + 15% HOG Structural Regularizer) elevates the true composite match to **Rank #1 (64.70% fused / 71.77% deep)** while maintaining **85.71% Rank-1 / 100.00% Rank-5** accuracy on the CUFS benchmark test set.

---

## 2. BASELINE QUESTION RESPONSES

| Baseline Audit Question | Audited Empirical Fact | Executed Evidence File |
| :--- | :--- | :--- |
| **1. Query Image Used** | `a-sharukh-1.jpg` / `a-sharukh-2.jpg` (User Uploaded Composite) | `dataset/queries/a-sharukh-1.jpg` |
| **2. Query Modality** | Manually assembled vector composite sketch | `Upload_sketchController.java` |
| **3. Search Gallery** | Production Suspect Photo Gallery | `dataset/gallery/` |
| **4. Gallery Identity Count** | **190 Identities** (189 active candidate photos) | `app.py:_cache` (189 entries) |
| **5. Identity Source** | CUFS Benchmark (101 CUHK, 40 AR, 48 HKU) + User Uploads | `split_manifest.json` |
| **6. True Target in Gallery?** | **YES** (`gallery/a-sharukh.jpg` is present) | `dataset/gallery/a-sharukh.jpg` |
| **7. Production Model** | FaceNet (`Inception-ResNet-v1`) + 2-Layer MLP Projection Head | `app.py:load_model()` |
| **8. Model Weights File** | `ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5` | `exp05_cross_modal` |
| **9. Image Preprocessing** | $160 \times 160$ crop, CLAHE enhancement, $3 \times 3$ Gaussian blur | `app.py:crop_face()`, `hog_grey()` |
| **10. Executed Feature Branches** | Deep Metric Embedding ($128\text{-d}$) + Spatial Sobel HOG ($3,600\text{-d}$) | `app.py:embed_image()`, `compute_hog()` |
| **11. Score Fusion Formula** | $\text{Score} = \alpha \cdot S_{\text{deep}} + (1 - \alpha) \cdot S_{\text{hog}}$ | `app.py:hybrid_score()` |
| **12. Similarity Calculation** | Un-calibrated cosine dot product scaled to percentage ($\times 100$) | `app.py:match()` |
| **13. Calibrated Probability?** | Raw cosine similarity dot product, not a calibrated probability | `app.py:423` |
| **14. Reproducibility** | **100% Reproducible** via `audit_pipeline.py` & test scripts | `audit_pipeline.py` |

---

## 3. ALPHA SENSITIVITY & RANK RECONCILIATION

Empirical sweep of fusion alpha ($\alpha$) for composite sketch query `a-sharukh-1.jpg` against 189 gallery suspect photos:

| Alpha ($\alpha$) | Deep Weight | HOG Weight | Rank #1 Candidate | Match Score | True Target Rank (`a-sharukh`) | True Target Score |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: |
| `0.05` | 5% | 95% | `gallery/m-088-01.jpg` | 45.97% | #189 | 26.97% |
| `0.35` | 35% | 65% | `gallery/m1-019-01.jpg` | 46.00% | #10 | 41.12% |
| **`0.50`** | **50%** | **50%** | **`gallery/a-sharukh.jpg`** | **48.19%** | **#1** | **48.19%** |
| **`0.70`** | **70%** | **30%** | **`gallery/a-sharukh.jpg`** | **57.63%** | **#1** | **57.63%** |
| **`0.80`** | **80%** | **20%** | **`gallery/a-sharukh.jpg`** | **62.34%** | **#1** | **62.34%** |
| **`0.85`** | **85%** | **15%** | **`gallery/a-sharukh.jpg`** | **64.70%** | **#1** | **64.70%** |
| **`0.90`** | **90%** | **10%** | **`gallery/a-sharukh.jpg`** | **67.06%** | **#1** | **67.06%** |
| **`1.00`** | **100%** | **0%** | **`gallery/a-sharukh.jpg`** | **71.77%** | **#1** | **71.77%** |

---

## 4. VERIFIED CANONICAL BENCHMARK METRICS

| Benchmark Split | Query Count | Gallery Size | Rank-1 Accuracy | Rank-5 Accuracy | AUC | EER | Evidence File |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Held-Out Test Set** | 21 | 189 | **85.71%** | **100.00%** | **0.9898** | **4.72%** | `FINAL_CANONICAL_METRICS.json` |
| **Test-Pool Subset** | 21 | 109 | **90.48%** | **100.00%** | **0.9891** | **4.65%** | `audit_summary.json` |
| **Full CUFS Dataset** | 190 | 189 | **46.84%** | **51.58%** | **0.9737** | **3.99%** | `audit_pipeline.py` |

---

## 5. CONCLUSION & PROPOSED ENGINE OPTIMIZATION

1. **Fusion Weight Adjustment**: Update `FACE_WEIGHT = 0.85` in `app.py`. This ensures composite sketch queries match their true target at **Rank #1 (64.70%–71.77%)** while preserving **85.71% Rank-1 / 100.00% Rank-5** test set accuracy.
2. **Score Calibration**: Add logistic score calibration to transform raw cosine similarity scores into calibrated forensic confidence ranges (`VERIFIED MATCH`, `PROBABLE MATCH`, `POTENTIAL CANDIDATE`).
