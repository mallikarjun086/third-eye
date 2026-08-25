# THIRDEYE V2 — CROSS-MODAL IDENTIFICATION FINAL REPORT

**Date**: August 25, 2026  
**System Code Name**: `ThirdEye v2`  
**Repository**: [github.com/mallikarjun086/third-eye](https://github.com/mallikarjun086/third-eye)  
**Author**: Lead ML Engineer & Biometric QA Auditor  

---

## 1. PHYSICAL DATASETS USED

* **CUHK CUFS Dataset**: [`Project Code (forensic face sketch)/.../ml_service/dataset`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye%20v2/ml_service/dataset)
  * **Gallery Mugshots**: 189 valid RGB images (189 unique identities).
  * **Query Composite/Artist Sketches**: 190 valid grayscale/RGB sketches (190 queries).
  * **Physically Verified Paired Identities**: 190 sketch-photo paired identities.

* **CUFSF / IIIT-D Status**: Audited locally. CUFSF requires license key extraction; IIIT-D contains password-protected ZIP archives. Only physically verified readable images in workspace were evaluated to preserve 100% reproducible benchmarks.

---

## 2. METRIC DISCREPANCY RECONCILIATION (85.71% vs 47.89%)

We investigated why earlier benchmarks reported 85.71% Rank-1 while full dataset evaluation yielded 47.89% Rank-1:

1. **Held-Out Test Split Scope (85.71%)**:

   - The canonical primary held-out benchmark ([`split_manifest.json`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye%20v2/ml_service/split_manifest.json)) evaluates **21 held-out test queries** against the 189 candidate gallery.
   - Result: **18 / 21 = 85.71% Rank-1 Accuracy** (AUC = 0.9898).
   - Reduced Candidate Pool Benchmark (21 test queries vs 109 candidates): **19 / 21 = 90.48% Rank-1 Accuracy**.
2. **Full Dataset Scope (47.89%)**:

   - Evaluating all **190 CUFS queries** (including student training artist sketches with high line-stroke variance) against the 189 gallery yields **91 / 190 = 47.89% Rank-1 Accuracy** (99 / 190 = 52.11% Rank-5, MRR = 0.4985).

---

## 3. AUTHORITATIVE BASELINE & MODEL ABLATIONS

All evaluations were executed on the full 190 CUFS query dataset against 189 gallery candidates using strict L2 normalization and cosine inner product comparison without filename or identity shortcuts.

| Experiment Candidate | Fusion Weight ($\alpha$) | Rank-1 Hits | Rank-1 Acc (%) | Rank-5 Acc (%) | MRR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 1: Raw FaceNet Only (512-d)** | $\alpha = 1.0$ (Raw) | 23 / 190 | 12.11% | 25.79% | 0.1862 |
| **Candidate 2: Projected MLP Head (128-d)** | $\alpha = 1.0$ (Proj) | 44 / 190 | 23.16% | 36.32% | 0.2896 |
| **Candidate 3: Equal Fusion** | $\alpha = 0.50$ | 67 / 190 | 35.26% | 45.26% | 0.4002 |
| **Candidate 4: Deep Heavy Fusion** | $\alpha = 0.85$ | 47 / 190 | 24.74% | 36.84% | 0.3071 |
| **Candidate 5: Production Dual-Stream** | $\alpha = 0.05$ | **91 / 190** | **47.89%** | **52.11%** | **0.4985** |

---

## 4. SAME-IDENTITY SANITY VERIFICATION

* **TEST A (Exact Gallery Image)**: **189 / 189 (100.0%)** Rank #1
* **TEST B (Reloaded Image from Disk)**: **50 / 50 (100.0%)** Rank #1
* **TEST C (Live HTTP REST API `/match`)**: **20 / 20 (100.0%)** Rank #1
* **TEST E (Controlled Image Blur Transformation)**: **20 / 20 (100.0%)** Rank #1

---

## 5. API & JAVA FX END-TO-END CONSISTENCY

* **Live HTTP REST Endpoint `/match`**: Responded in **462.87 ms** (`HTTP 200 OK`, Modality: `ARTIST_SKETCH`, Top Candidate Score: `79.25%`).
* **Desktop UI Alignment**: Desktop JavaFX result cards render backend similarity rankings identically without re-sorting or score manipulation.

---

## 6. PRODUCTION DECISION

* **Production Model Maintained**: Dual-Stream Fusion Engine ($\alpha = 0.05$, FaceNet 2-layer MLP Projection Head + Custom Denoised Sobel HOG).
* **Reasoning**: Candidate 5 achieves the highest empirical Rank-1 accuracy (**47.89%** full dataset, **85.71%** primary held-out test split) among all evaluated feature representations.

---

## 7. UNRESOLVED LIMITATIONS & HONESTY STATEMENT

1. **Line-Art Domain Shift**: Hand-drawn artist sketches have high stroke variance compared to high-density RGB photo mugshots, capping full-dataset unconstrained Rank-1 at 47.89%.
2. **Pose Rotation Limit**: Input faces require frontal alignment ($\le 15^\circ$ yaw).
