# RESEARCH PAPER REFERENCE 05

## Forensic Face Sketch Construction and Recognition

* **Authors**: S. Pushpalatha, Shashank V, Shreyank K. J., Sri Ranga B. K., and Pavan T. M.
* **Affiliation**: Department of Information Science and Engineering, Dayananda Sagar College of Engineering, Bengaluru, India
* **Journal**: *International Journal for Research in Applied Science & Engineering Technology (IJRASET)*
* **Volume & Issue**: Volume 13, Issue XII, December 2025

---

### Executive Abstract

This paper presents a desktop-based software solution designed to bridge the gap between eyewitness recall and offender identification. The system combines a composite face sketching module with a facial recognition matching framework. Eyewitnesses work alongside law enforcement officers to piece together facial feature layers (eyes, nose, hair, mouth, jawline), after which a convolutional neural network extracts spatial feature maps to compare against registered police mugshots.

---

### Key Technical Contributions & Features

1. **Facial Feature Assembly Interface**:
   * Graphical canvas enabling drag-and-drop layering of facial features from pre-classified image directories.

2. **Convolutional Feature Extraction**:
   * Uses deep feature maps extracted from standardized convolutional layers to represent composite face sketches.

3. **Cosine Similarity Ranking**:
   * Computes distance metrics between sketch feature vectors and stored photographic database representations to produce a ranked list of potential suspects.

---

### Critical Analysis & Comparison with ThirdEye v2

| Evaluation Dimension | Pushpalatha et al. (2025) | ThirdEye v2 (Your Project) |
| --- | --- | --- |
| **Feature Backbone** | Standard CNN feature extraction | Inception-ResNet-v1 (FaceNet) + Custom MLP Head |
| **Domain Gap Optimization** | Direct CNN distance matching | Triplet Margin Loss ($\text{margin}=0.3$) projection |
| **Spatial Descriptor** | Unweighted global feature map | Elliptical Masked CLAHE-HOG (3,600 dimensions) |
| **Score Fusion Engine** | Single feature similarity score | Weighted Late Fusion ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$) |
| **Empirical Benchmarks** | Standard baseline metrics | **85.71% Rank-1** (Primary) / **90.48%** (Secondary pool) |
