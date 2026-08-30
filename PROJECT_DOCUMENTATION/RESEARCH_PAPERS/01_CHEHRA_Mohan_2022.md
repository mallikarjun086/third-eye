# RESEARCH PAPER REFERENCE 01

## CHEHRA: An Application for Forensic Face Sketch Construction and Recognition

* **Authors**: Aditi Mohan, Sejal Matekar, and Prof. Prashant Itankar
* **Affiliation**: Department of Computer Engineering, Datta Meghe College of Engineering, Navi Mumbai, India
* **Journal**: *International Journal of Advanced Research in Science, Communication and Technology (IJARSCT)*
* **Volume & Issue**: Volume 2, Issue 2, April 2022
* **DOI**: [10.48175/IJARSCT-3179](https://doi.org/10.48175/IJARSCT-3179)

---

### Executive Abstract

Traditional forensic face sketch construction relies heavily on the availability of skilled forensic artists and manual drawing techniques, which are often time-consuming and subjective. The CHEHRA project presents an integrated digital platform that enables law enforcement officers to construct composite facial sketches through an intuitive drag-and-drop web interface. Once assembled, the system utilizes cloud-based biometric image recognition services (specifically AWS Rekognition) to compare composite line sketches against registered criminal mugshot photo databases.

---

### Key Technical Contributions & Features

1. **Web-Based Drag-and-Drop Sketch Workstation**:
   * Offers pre-drawn facial component libraries (hair, eyes, eyebrows, nose, lips, chin, jawline).
   * Allows non-artist police personnel to construct suspect composites based on eyewitness memory.

2. **Cloud Biometric Matching Integration**:
   * Sends compiled composite image streams to cloud-hosted computer vision engines (AWS Rekognition).
   * Computes facial feature similarity vectors against a centralized criminal database.

3. **System Security & Access Controls**:
   * Implements machine locking and two-step authentication mechanisms to safeguard sensitive case files.

---

### Critical Analysis & Comparison with ThirdEye v2

| Evaluation Dimension | CHEHRA (Mohan et al., 2022) | ThirdEye v2 (Your Project) |
| --- | --- | --- |
| **Architecture** | Web application backed by Cloud APIs | Local desktop workstation (JavaFX + Python FastAPI) |
| **Data Privacy** | High vulnerability (sends sketches to AWS public cloud) | 100% Offline & Air-gapped (zero data leakage) |
| **Domain Gap Handling** | Generic cloud facial recognition (unoptimized for sketches) | Metric-Learned MLP Projection Head (Triplet Margin Loss) |
| **Score Fusion** | Single cloud confidence score | Dual-Stream Late Fusion ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$) |
| **Rank-1 Accuracy** | Qualitative evaluation | **85.71% Rank-1** (Primary 189-candidate gallery) |
