# LEGACY COMPONENT DECISION: THIRDEYE_FACEMATCH

**Decision Date**: August 23, 2026  

---

## 1. Classification & Status

* **Component Path**: [`Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye_FaceMatch`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye_FaceMatch)
* **Technology**: Java Swing + AWS Rekognition API
* **Current Operational Role**: **SUPERSEDED / LEGACY PROTOTYPE**

---

## 2. Rationale & Decision: OPTION B (ARCHIVE IN REPOSITORY)

### Rationale for Decision

1. **Zero Runtime Dependency**: `ThirdEye v2` does NOT call, depend on, or reference `ThirdEye_FaceMatch`.
2. **Historical Engineering Evidence**: Retaining this folder in the repository provides proof of project evolution to final-year project examiners (demonstrating how Phase 1 cloud API limitations led to Phase 2 custom offline deep learning models in `ThirdEye v2`).

### Action Taken

* Retained in repository as an **Archived Prototype**.
* Documentation explicitly notes: **"NOT PART OF CURRENT PRODUCTION SYSTEM"**.
