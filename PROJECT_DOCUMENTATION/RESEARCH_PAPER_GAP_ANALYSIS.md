# RESEARCH PAPER & APPLICATION GAP ANALYSIS

## ThirdEye v2 vs. Key Literature (2022–2025)

**Project Title**: AI-Based Forensic Face Sketch and Recognition System (`ThirdEye v2`)  
**Analysis Date**: August 30, 2026  
**Target Goal**: Evaluation against 6 referenced papers, identifying strengths, application gaps, and research enhancements.

---

## 1. Summary of 6 Referenced Papers

| # | Paper Reference | Primary Methodology | Key Strengths | Key Limitations |
| --- | --- | --- | --- | --- |
| **1** | **CHEHRA** (Mohan et al., *IJARSCT*, Apr. 2022) | Web-based drag-and-drop sketch tool + AWS Rekognition API. | Simple web interface; automated cloud matching. | Requires active internet/cloud (privacy risk); no custom cross-modal projection model. |
| **2** | **RecogniPro** (Shaikh et al., *IJCRT*, Mar. 2024) | Web composite sketch creation + deep learning matching on cloud photo database. | Drag-and-drop UI; cloud integration. | Dependent on cloud connectivity; lacks spatial feature fusion. |
| **3** | **Heterogeneous Sketch Recognition** (Itole et al., *IJECE*, 2024) | **X-Bridge** framework using GAN sketch-to-photo synthesis + soft biometrics (age/gender). | Uses GAN image translation to bridge domain gap; incorporates soft biometrics. | High computational cost; GAN hallucination risks altering facial identity details. |
| **4** | **Generative Neural Networks** (Sádaba-Campo & Gómez-Moreno, *BDCC*, 2025) | Text-to-Image & Image-to-Image Generative AI (Stable Diffusion, GANs, VAEs, ControlNet). | Produces photorealistic faces from text descriptions. | High risk of AI hallucination/bias; not legally admissible in court due to non-deterministic generation. |
| **5** | **Forensic Face Sketch** (Pushpalatha et al., *IJRASET*, Dec. 2025) | Basic element composite assembly + standard CNN feature extraction. | Straightforward workflow for basic sketch creation. | Uses raw CNN features with low cross-modal accuracy (high domain gap drop). |
| **6** | **AI-Driven Forensic Sketch** (Pasunuri et al., *ICCSCE / Springer*, 2025) | Recommendation engine for composite facial elements + visual side-by-side feature highlighting. | Recommends compatible features; visual heatmap matching. | Cloud dependency; lack of empirical fusion parameter optimization ($\alpha$ weighting). |

---

## 2. Comparative Matrix: ThirdEye v2 vs. Literature

| Architectural Feature | Literature Status (Papers 1–6) | **ThirdEye v2 (Your App)** | Verdict / Advantage |
| --- | --- | --- | --- |
| **Deployment & Security** | Mostly Cloud-based (AWS, cloud servers) | **100% Offline / Local Desktop (JavaFX + FastAPI)** | **ThirdEye v2 Advantage**: Complies with law enforcement data privacy policies. |
| **Domain Gap Adaptation** | Raw CNNs or GAN translation | **Dual-Stream: FaceNet + MLP Projection Head + Spatial CLAHE-HOG** | **ThirdEye v2 Advantage**: Custom 2-layer MLP projection head boosts Rank-1 accuracy from 12.11% to 85.71%. |
| **Score Fusion Strategy** | Single feature vector or GAN image | **Late Score Fusion ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$)** | **ThirdEye v2 Advantage**: Combines semantic embeddings with local spatial geometry. |
| **Sketch Creation Mode** | Component assembly OR Generative AI | **Deterministic Component Assembly** | **ThirdEye v2 Advantage**: Court-admissible; preserves exact eyewitness memory without AI hallucinations. |
| **Benchmarked Accuracy** | Qualitative or basic accuracy | **85.71% Rank-1 (189 gallery) / 90.48% (109 test pool) / 92.0% (100 pair)** | **ThirdEye v2 Advantage**: Rigorous quantitative metrics documented in canonical JSON. |

---

## 3. Gaps Filled by ThirdEye v2 (Your Strengths over Literature)

1. **Elimination of Cloud Dependency & Data Leakage (vs. Mohan et al. & Shaikh et al.)**:
   - Papers 1 and 2 rely on external cloud APIs (e.g., AWS Rekognition). Uploading confidential forensic suspect sketches to third-party clouds violates police data protection norms. `ThirdEye v2` operates entirely offline via a localized JavaFX-FastAPI architecture.

2. **Solving the Cross-Modal Domain Gap without GAN Hallucinations (vs. Itole et al. & Sádaba-Campo et al.)**:
   - Generative approaches (GANs/Diffusion) generate photorealistic images but introduce artificial facial features (hallucinations) that alter the criminal's true identity. `ThirdEye v2` retains the raw sketch geometry while projecting deep embeddings into a shared metric subspace via Triplet Margin Loss.

3. **Hybrid Late Score Fusion (vs. Pushpalatha et al. & Pasunuri et al.)**:
   - Standard facial recognition backbones fail on line sketches (FaceNet alone yields only 12.11% Rank-1 accuracy). `ThirdEye v2` fuses deep semantic projections with spatially-masked CLAHE HOG descriptors (3,600-d), achieving an 85.71% Rank-1 retrieval rate.

---

## 4. Gaps in Your Application (What You Should Add / Improve)

To make your application and paper tier-1 publication-ready (Q1/Q2 Scopus journals or IEEE conferences), address the following technical and research gaps:

### A. Technical & Application Gaps

1. **Soft Biometric Pre-Filtering (Demographic Filter Gap)**:
   - *Current State*: `ThirdEye v2` searches the entire candidate gallery for every query.
   - *Gap*: When candidate databases scale to 100,000+ mugshots, searching every image becomes slow.
   - *Fix*: Implement soft biometric filtering (Gender, Age Range, Skin Tone, Facial Hair) to trim the search space by 80–90% before running score fusion (as demonstrated by Itole et al., 2024).

2. **Explainable AI (XAI) & Visual Heatmaps (Feature Highlight Gap)**:
   - *Current State*: Returns top-$K$ candidates with a numerical similarity percentage (e.g., `87.4%`).
   - *Gap*: Forensic investigators need to see *where* the match came from.
   - *Fix*: Add visual saliency maps (Grad-CAM on the projection head or HOG cell comparison overlays) highlighting matching facial regions (eyes, nose, mouth) side-by-side (inspired by Pasunuri et al., 2025).

3. **Facial Feature Recommendation Engine**:
   - *Current State*: The user manually selects hair, eyes, nose, mouth from menus.
   - *Gap*: Users may choose proportional mis-matches (e.g., oversized eyes with a tiny face contour).
   - *Fix*: Add an intelligent recommendation rule engine that suggests compatible facial components based on previously selected elements.

4. **Optional GAN/ControlNet Colorization Pipeline**:
   - *Current State*: Sketch output is strictly black-and-white line art.
   - *Gap*: Eyewitnesses often remember color cues (skin tone, hair color, eye color).
   - *Fix*: Provide an optional post-processing toggle for automatic skin-tone colorization or ControlNet refinement without altering structural line landmarks.

---

### B. Research & Paper Presentation Gaps

1. **Multi-Dataset Benchmarking (Domain Diversity Gap)**:
   - *Current State*: Benchmark evaluation relies primarily on CUFS dataset identities.
   - *Fix*: Evaluate your trained model on additional public datasets:
     - **IIIT-D Forensic Sketch Database** (real forensic sketches by professional artists).
     - **e-PRIP / PRIP Composite Sketch Database** (software-generated composites).
     - **CUFSF Database** (includes non-linear lighting & facial expression variations).

2. **Modern Feature Extractor Backbones Comparison**:
   - *Current State*: Uses `Inception-ResNet-v1` (FaceNet) as the base backbone.
   - *Fix*: Add an ablation study comparing **FaceNet vs. ArcFace (InsightFace / ResNet-50)** and **AdaFace** backbones to justify your choice.

3. **Statistical Significance & Confidence Interval Analysis**:
   - *Current State*: Reports point-estimate accuracy (e.g., 85.71%).
   - *Fix*: Calculate 95% Confidence Intervals (CI) and perform paired $t$-tests ($p < 0.05$) to prove statistical superiority over standard baselines.

---

## 5. Actionable Roadmap to Elevate Your Project & Paper

```text
[ Phase 1: Code Enhancements ]
├── Add Demographic Pre-Filtering (Gender, Age, Facial Hair)
├── Add Visual Feature Matching Heatmap (Grad-CAM / HOG Difference)
└── Add Feature Recommendation Engine to JavaFX Client

[ Phase 2: Experimental Validation ]
├── Run Evaluation on IIIT-D Forensic Sketch Database
├── Add ArcFace vs. FaceNet Embedding Comparison
└── Compute 95% Confidence Intervals & p-values

[ Phase 3: Paper Manuscript Writing ]
└── Format in IEEE Transactions / Springer LNCS Template using the Comparative Matrix
```
