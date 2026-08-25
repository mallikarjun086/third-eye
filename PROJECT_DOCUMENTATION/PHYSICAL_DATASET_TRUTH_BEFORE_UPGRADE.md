# PHYSICAL DATASET TRUTH BEFORE UPGRADE

**Audit Timestamp**: 2026-08-24T13:36:00Z  
**Audit Scope**: Recursive Filesystem Physical Inspection of `ThirdEye v2`  

---

## 1. Physical Dataset Inventory

| Dataset Name | Local Path | Physical Image Files | Unique Identities | Sketch Count | Photo Count | Paired Sketch-Photo IDs | Physical Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **CUFS (CUHK Student)** | `ml_service/dataset/` | 276 | 188 | 88 | 188 | 88 | **`PHYSICALLY_VERIFIED`** |
| **ThirdEye Composite Bench** | `ml_service/dataset/queries/` | 2 | 1 | 2 | 1 | 1 | **`PHYSICALLY_VERIFIED`** |
| **CUFSF (CUHK FERET)** | `data/cufsf/` | 0 | 0 | 0 | 0 | 0 | **`NOT INTEGRATED — ACCESS PENDING`** |
| **IIIT-D Composite** | `data/iiitd/` | 0 | 0 | 0 | 0 | 0 | **`NOT INTEGRATED — ACCESS PENDING`** |
| **LFW Distractors** | `data/lfw/` | 0 | 0 | 0 | 0 | 0 | **`NOT INTEGRATED — NETWORK RESTRICTED`** |

---

## 2. Verified Physical Findings

1. **CUFS Dataset**: Physically present under `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/`. Contains 188 photo images in `gallery/` and 88 sketch query images in `queries/`.
2. **ThirdEye Composite Benchmark**: 2 internal composite sketch queries (`a-sharukh-1.jpg` and `a-sharukh-2.jpg`) with ground truth target identity `a-sharukh`.
3. **CUFSF & IIIT-D**: No physical image files exist in `data/cufsf/` or `data/iiitd/`. README files and adapters exist to facilitate dataset ingestion once physical archives are placed by the user.
4. **Network Access Bounds**: Direct automatic dataset downloading via outbound HTTP in the local sandbox returns `[Errno 11001] getaddrinfo failed`. Physical downloads must be manually placed by the user under `data/`.
