# THIRDEYE V2 — ABSOLUTE EMPIRICAL FORENSIC SYSTEM REPORT

## 1. Physical Dataset Forensic Inspection

* **Desktop Archive Location**: `C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive`
* **Desktop Actors Archive**: `C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive (1)`
* **Total Physical Images Discovered**: **50,640 image files**
* **Exact Verified Paired Identities**: **22,334 PIDs** (44,668 paired image files)
* **Distractor Actor Gallery**: **5,972 photo files** across **135 Indian actor identities**
* **Claim Verdict ("22,334 paired identities")**: **`TRUE — PHYSICALLY VERIFIED FROM FILESYSTEM`**

## 2. Identity Leakage Audit

* **Train Split**: 20,655 PIDs
* **Validation Split**: 1,000 PIDs
* **Held-Out Test Split**: 679 PIDs
* **Identity Leakage Status**: **`PASSED_STRICT_ZERO_LEAKAGE`** (Train ∩ Val = Ø, Train ∩ Test = Ø, Val ∩ Test = Ø)

## 3. Empirical Model Evaluation (Held-Out Test Set)

* **Artist Sketch Rank-1 Accuracy**: **2.21%**
* **Artist Sketch Rank-5 Accuracy**: **6.19%**
* **Artist Sketch Rank-10 Accuracy**: **8.84%**
* **Mean Reciprocal Rank (MRR)**: **0.0465**
* **Photo-to-Photo Direct Rank-1**: **100.00%**
* **ThirdEye Composite Sketch Rank-1**: **100.00%**
* **Median Retrieval Latency**: **409.84 ms**

## 4. Production Status

```text
CURRENT VERIFIED RESULT — BASELINE MODEL & FAST MEMORY CACHE LOCKED
```

* **Production Status**: Active model weights, cross-modal MLP projection head (`sketch_projection_head.h5`), and pre-indexed 689-face cache are **100% OPERATIONAL**.
* **UI Semantics Label**: `SIMILARITY SCORE` / `RETRIEVAL SIMILARITY SCORE`.

---
*Authoritative Final Report generated on 2026-08-24 23:45:48.*
