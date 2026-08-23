# COMPOSITE SKETCH BENCHMARK VALIDITY & SAMPLE SIZE LIMITATIONS REPORT

**Audit Date**: August 24, 2026  
**Audited Modality**: ThirdEye JavaFX Eyewitness Vector Composite Sketches  
**Current Sample Size**: 2 Known Ground-Truth Queries (`a-sharukh-1.jpg`, `a-sharukh-2.jpg`)  

---

## 1. OFFICIAL CLAIM TERMINOLOGY & STATISTICAL DISCLAIMER

> [!IMPORTANT]
> **Official Approved Claim**:
> **`INTERNAL COMPOSITE ACCEPTANCE RESULT: 2/2 known-ground-truth queries retrieved at Rank-1`**

> [!WARNING]
> **Statistical Limitation & Disclaimer**:
> A sample size of 2 composite queries is **statistically insufficient** to declare a general 100% forensic recognition accuracy. Results represent an internal software acceptance test verifying that the composite sketch pipeline correctly retrieves ground-truth targets without impostor misranking.

---

## 2. GROUND-TRUTH COMPOSITE QUERY AUDIT TABLE

| Query ID | Ground-Truth PID | Query SHA256 Checksum | Generation Config | Gallery Manifest | Deep Score | HOG Score | Fused Score | Rank |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `a-sharukh-1.jpg` | `a-sharukh` | `c623910c5c363d6f030a52f9bc952fdf...` | ThirdEye JavaFX Vector Canvas | `v2.0-canonical` | 71.77% | 24.61% | **64.70%** | **#1** |
| `a-sharukh-2.jpg` | `a-sharukh` | `a827419e4d580f4f9dbcfb9e289e65bd...` | ThirdEye JavaFX Vector Canvas | `v2.0-canonical` | 74.50% | 25.10% | **67.09%** | **#1** |
