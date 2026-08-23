# ML EXPERIMENT LINEAGE & RESEARCH TRACKING

**System Code Name**: `ThirdEye v2`  

---

## 1. Sequential Experiment Evolution Track

```text
[ Raw Baseline: exp04_embedding ] ──> [ Face Alignment: exp01_alignment ] ──> [ Preprocessing: exp02_preprocessing ]
                                                                                         │
                                                                                         ▼
[ Production Engine: app.py ] <── [ Score Fusion: exp06_fusion ] <── [ Metric Learning: exp05_cross_modal ] <── [ Feature HOG/LBP: exp03_hog_lbp ]
```

---

## 2. Detailed Experiment Lineage Table

| Exp ID | Folder Path | Hypothesis / Focus | Key Finding / Outcome | Used in Production? |
| :--- | :--- | :--- | :--- | :---: |
| **`exp01`** | `experiments/exp01_alignment` | Evaluate MediaPipe landmark-based face alignment | Alignment improves bounding box consistency. | **YES** |
| **`exp02`** | `experiments/exp02_preprocessing` | Compare CLAHE vs Histogram Equalization vs Blur | CLAHE (`clipLimit=2.0`, `tileGridSize=(8,8)`) + $3 \times 3$ blur provides optimal contrast. | **YES** |
| **`exp03`** | `experiments/exp03_hog_lbp` | Evaluate classical HOG vs LBP spatial descriptors | Sobel HOG with elliptical face masking outperforms LBP for line sketches. | **YES** |
| **`exp04`** | `experiments/exp04_embedding` | Measure raw FaceNet cross-modal domain gap | Standalone raw FaceNet achieves only **12.11% Rank-1** accuracy across full dataset. | Baseline Diagnostic |
| **`exp05`** | `experiments/exp05_cross_modal` | Train 2-layer MLP Projection Head via Triplet Loss | Boosted deep embedding Rank-1 accuracy to **65.00%** on validation split (164k params). | **YES** |
| **`exp06`** | `experiments/exp06_fusion` | Grid search late fusion weighting hyperparameter $\alpha$ | Optimal production fusion weight established at **$\alpha^* = 0.05$** ($5\%\text{ Deep} + 95\%\text{ HOG}$). | **YES** |
| **`exp07`** | `experiments/exp07_final_eval` | Benchmark held-out test split against gallery | Achieved **85.71% Rank-1** (189 gallery) and **90.48% Rank-1** (109 gallery). | **YES (Canonical Benchmark)** |
