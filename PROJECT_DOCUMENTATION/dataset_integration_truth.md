# DATASET INTEGRATION TRUTH & LEGAL AUDIT REPORT

**Audit Date**: August 24, 2026  
**Audited Datasets**: CUFS, CUFSF, IIIT-D, ThirdEye Composite  

---

## 1. MANDATORY INTEGRATION DECLARATION

> [!IMPORTANT]
> **Canonical Integration Statement**:
> **`NO LARGE FORENSIC/COMPOSITE DATASET IS CURRENTLY INTEGRATED`**
>
> Large academic datasets (CUFSF with 1,194 PIDs and IIIT-D with 459 PIDs) require signed academic research agreements and are not physically present in local storage. Acquisition instructions are available in [`data/README.md`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/data/README.md).

---

## 2. PHYSICAL DATASET AUDIT MATRIX

| Dataset Name | Physical Path | Legal Access Status | Total Files | Valid Images | Unique PIDs | Sketches | Photos | Paired PIDs | Usage |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **CUFS (CUHK)** | `ml_service/dataset/` | Open Academic | 381 | 381 | **190 PIDs** | 191 | 190 | 189 | Train (60), Val (20), Test (21), Gallery (189) |
| **CUFSF (FERET)** | `data/cufsf/` | License Required | 0 | 0 | 0 | 0 | 0 | 0 | `NOT INTEGRATED — ACCESS PENDING` |
| **IIIT-D Forensic** | `data/iiitd/` | License Required | 0 | 0 | 0 | 0 | 0 | 0 | `NOT INTEGRATED — ACCESS PENDING` |
| **ThirdEye Composite** | `ml_service/dataset/` | Internal | 2 | 2 | **2 PIDs** | 2 | 0 | 2 | Internal Acceptance Test Only |
