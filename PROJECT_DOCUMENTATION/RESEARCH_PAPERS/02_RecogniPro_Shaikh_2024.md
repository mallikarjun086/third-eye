# RESEARCH PAPER REFERENCE 02

## RecogniPro: Recognition and Construction of Forensic Facial Sketches

* **Authors**: Prof. Nisar S. Shaikh, Devika Wagh, Samruddhi Takawale, Prachi Singh, and Abhishek Jadhav
* **Affiliation**: Department of Computer Engineering, Pune District Education Association's College of Engineering, Pune, India
* **Journal**: *International Journal of Creative Research Thoughts (IJCRT)*
* **Volume & Issue**: Volume 12, Issue 3, March 2024
* **Paper ID**: IJCRT2403257

---

### Executive Abstract

RecogniPro introduces a digital framework for facial sketch generation and mugshot matching to streamline criminal investigations. Addressing the limitations of manual forensic portraiture—such as artist availability, high latency, and subjective bias—RecogniPro pairs a component-based GUI with deep learning feature extraction pipelines to query suspect databases. The system focuses on modular software execution to assist law enforcement officers in compiling facial composites from eyewitness testimony.

---

### Key Technical Contributions & Features

1. **Modular Composite Construction**:
   * Graphical canvas enabling drag-and-drop placement, scaling, and positioning of facial feature elements.
   * Categorized component library organized by facial anatomy (facial shape, eyes, nose, mouth, hair styles).

2. **Deep Learning Matching Pipeline**:
   * Uses deep convolutional neural network (CNN) feature vectors to compare assembled composite sketches against photo mugshots.
   * Measures feature distance between sketch line-art and photograph RGB color channels.

3. **Cloud Infrastructure Integration**:
   * Connects local clients to cloud storage repositories for centralized criminal records management.

---

### Critical Analysis & Comparison with ThirdEye v2

| Evaluation Dimension | RecogniPro (Shaikh et al., 2024) | ThirdEye v2 (Your Project) |
| --- | --- | --- |
| **Deployment Mode** | Cloud-assisted Client/Server | 100% Offline Standalone Desktop Workstation |
| **Feature Extractor** | Standard CNN feature maps | Deep Metric FaceNet (128-d MLP Projection Head) |
| **Spatial Descriptor** | None | 3,600-dimensional CLAHE HOG Spatial Descriptor |
| **Domain Gap Adaptation** | Basic CNN distance matching | Metric Triplet Loss ($\text{margin}=0.3$) Optimization |
| **Benchmarked Accuracy** | Basic recognition rates | **85.71% Rank-1** (Primary 189-candidate gallery) |
