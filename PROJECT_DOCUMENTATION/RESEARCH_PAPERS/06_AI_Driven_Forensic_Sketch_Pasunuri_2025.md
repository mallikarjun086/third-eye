# RESEARCH PAPER REFERENCE 06

## AI-Driven Forensic Face Sketch Construction and Recognition

* **Authors**: Kathyayini Pasunuri, Cheera Rohan, Gillala Vaishak Reddy, and Talla Sai Sree
* **Affiliation**: Department of Artificial Intelligence and Data Science, Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad, India
* **Conference & Publisher**: *International Conference on Computer Science and Communication Engineering (ICCSCE 2025)*, Atlantis Press (Part of Springer Nature)
* **Volume & Date**: Advances in Computer Science Research, vol. 124, April 2025 (Published Online Nov 2025)
* **DOI**: [10.2991/978-94-6463-858-5_231](https://doi.org/10.2991/978-94-6463-858-5_231)

---

### Executive Abstract

Pasunuri et al. propose an AI-assisted framework designed to minimize human bias and proportional distortions in forensic composite sketching. Beyond traditional element selection, their platform incorporates an **AI Feature Recommendation Engine** that dynamically suggests compatible facial components (e.g., matching nose bridge width to selected eye spacing) to maintain natural anatomical proportions. For recognition, the system pairs deep embedding extraction with a side-by-side visual comparison tool that highlights matching facial regions in color to aid forensic investigators.

---

### Key Technical Contributions & Features

1. **Intelligent Feature Recommendation Engine**:
   * Recommends anatomically proportional facial components based on prior feature choices during sketch construction.

2. **Visual Feature Comparison & Heatmaps**:
   * Provides side-by-side visual comparison between composite sketches and candidate mugshots, highlighting matching anatomical zones.

3. **Cloud-Supported Identification Engine**:
   * Connects local clients to deep learning models hosted on scalable cloud infrastructure.

---

### Critical Analysis & Comparison with ThirdEye v2

| Evaluation Dimension | Pasunuri et al. (ICCSCE 2025) | ThirdEye v2 (Your Project) |
| --- | --- | --- |
| **Element Selection** | Component assembly + AI Recommendation Engine | Deterministic component-based menu selection |
| **Visual Explainability** | Side-by-side visual matching color highlights | Candidate mugshot display + confidence percentage |
| **Score Fusion Engine** | Cloud deep neural embeddings | Dual-Stream Late Fusion ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$) |
| **Deployment Mode** | Cloud-assisted microservice architecture | **100% Offline & Air-gapped JavaFX + FastAPI** |
| **Rank-1 Benchmark** | Qualitative & baseline matching validation | **85.71% Rank-1** (Primary 189-candidate gallery) |
