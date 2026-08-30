# RESEARCH PAPER REFERENCE 03

## Heterogeneous Sketch-Face Photo Recognition in Forensic Science Laboratories

* **Authors**: Devendra A. Itole, M. P. Sardey, and Milind P. Gajare
* **Affiliation**: Department of Electronics and Telecommunication Engineering, COEP Technological University, Pune, India
* **Journal**: *International Journal of Electronics and Communication Engineering (IJECE)* / *IJEEE*
* **Volume & Issue**: Volume 11, Issue 8, pp. 260–268, 2024

---

### Executive Abstract

Matching heterogeneous face sketches against optical photographs presents a severe modality gap due to missing texture, color, and lighting cues in hand-drawn line sketches. Itole et al. propose the **X-Bridge Framework**, an AI-driven image translation architecture leveraging Generative Adversarial Networks (GANs) to bridge the cross-modal domain gap. The system converts raw input sketches into synthetic RGB face photos before performing biometric feature comparison, while incorporating soft biometric attributes (age, gender, ethnicity) to narrow candidate search spaces.

---

### Key Technical Contributions & Features

1. **X-Bridge GAN Image Translation Engine**:
   * Uses image-to-image GAN architectures to translate sparse black-and-white line sketches into photorealistic RGB mugshots.
   * Minimizes perceptual loss between synthesized photos and real database photographs.

2. **Soft Biometric Filtering**:
   * Integrates demographic parameters (age group, gender, facial hair) to filter out irrelevant database candidates prior to neural feature extraction.

3. **Multi-Modal Thermal & Sketch Analysis**:
   * Evaluates cross-modal performance across thermal-to-visible and sketch-to-photo matching scenarios in forensic science laboratories.

---

### Critical Analysis & Comparison with ThirdEye v2

| Evaluation Dimension | X-Bridge (Itole et al., 2024) | ThirdEye v2 (Your Project) |
| --- | --- | --- |
| **Cross-Modal Approach** | Generative Image-to-Image Synthesis (GAN) | Dual-Stream Projection Subspace & Spatial HOG Fusion |
| **Identity Preservation** | Vulnerable to GAN hallucination & feature distortion | Preserves exact structural geometry without AI distortion |
| **Computational Burden** | High GPU compute required for GAN translation | High-speed warm matching latency (**307.90 ms median**) |
| **Demographic Filtering** | Soft biometric pre-filtering integrated | Full gallery score fusion ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$) |
| **Legal Admissibility** | Synthetic photos may face legal scrutiny in court | Deterministic component assembly is fully court-admissible |
