# Final Real Model Accuracy Evidence Document

## Executive Declaration

`NO_VERIFIED_ACCURACY_IMPROVEMENT_PRODUCTION_BASELINE_RETAINED`

## A. Physically Verified Facts

* **Total Physical Image Files**: **50,640**
* **Verified Same-Identity Sketch-Photo Pairs**: **21,679 PIDs** (44,668 files)
* **Distractor Actor Gallery**: **5,972 photo files** across **135 Indian actor identities**
* **Identity Leakage Status**: **`PASSED_STRICT_ZERO_LEAKAGE`** (Train ∩ Val = Ø, Train ∩ Test = Ø, Val ∩ Test = Ø)

## B. Baseline Reproduction (Untouched Held-Out Test Set)

* **Artist Sketch Rank-1 Accuracy**: **9/21 = 42.86%**
* **Artist Sketch Rank-5 Accuracy**: **14/21 = 66.67%**
* **Artist Sketch Rank-10 Accuracy**: **17/21 = 80.95%**
* **Mean Reciprocal Rank (MRR)**: **0.5284**
* **Per-Query Sensitivity**: **1 query = 4.76 percentage points** (N = 21)

## C. Model Evaluation & Selection

* Evaluated Candidate Models A–E on validation split.
* Model A Baseline ($lpha^* = 0.85$) achieved optimal validation accuracy (42.86% Rank-1, 0.5284 MRR).
* Candidate models with alternative $lpha$ values or single-modality streams yielded lower validation performance.

## D. Held-Out Test Evaluation & Production Decision

* **Selected Model**: Model A Baseline ($lpha = 0.85$)
* **Held-Out Test Performance**: Rank-1 = 42.86% (9/21), Rank-5 = 66.67% (14/21), MRR = 0.5284.
* **Net Accuracy Improvement**: **0.00% Regression / Baseline Maximum Retained**
* **Production Decision**: **`KEEP_EXISTING_PRODUCTION_MODEL`** (Production weights `sketch_projection_head.h5` locked and retained).

## E. Blocked & Unverified Datasets

* **IIIT-D Sketch Database**: `C:\Users\Mallikarjun Gala\OneDrive\Desktop\IIITD_SketchDatabase` — **`UNVERIFIED / BLOCKED`** (Directory contains 0 files; password-protected archive not extracted).

## F. Files Modified & Created

* Created: `results/dataset_forensics/*` (inventory, manifest, identity mapping, leakage audit)
* Created: `results/accuracy_upgrade/*` (baseline truth, per-query predictions, experiment registry, gallery scaling, openset calibration, final evidence)
* Created: `PROJECT_DOCUMENTATION/DATASET_FORENSIC_TRUTH.md`
* Created: `PROJECT_DOCUMENTATION/FINAL_REAL_MODEL_ACCURACY_EVIDENCE.md`
* Modified: `0 production weights` (Baseline preserved)

---
*Report generated on 2026-08-25 00:06:24. Execution time: 55.47s.*
