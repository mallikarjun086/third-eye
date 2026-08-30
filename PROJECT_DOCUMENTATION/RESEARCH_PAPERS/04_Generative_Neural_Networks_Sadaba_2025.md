# RESEARCH PAPER REFERENCE 04

## Exploration of Generative Neural Networks for Police Facial Sketches

* **Authors**: Nerea Sádaba-Campo and Hilario Gómez-Moreno
* **Affiliation**: Department of Signal Theory and Communications, University of Alcalá, Madrid, Spain
* **Journal**: *Big Data and Cognitive Computing (BDCC)*
* **Volume & Publication Date**: Volume 9, Issue 2, February 2025
* **Publisher**: MDPI

---

### Executive Abstract

Sádaba-Campo and Gómez-Moreno evaluate the paradigm shift from traditional manual/composite police sketching to modern Generative Artificial Intelligence (GenAI). The authors conduct an empirical exploration of state-of-the-art generative neural network architectures—including Generative Adversarial Networks (GANs), Variational Autoencoders (VAEs), and Latent Diffusion Models (specifically Stable Diffusion, DALL-E 2/3, Midjourney, and ControlNet)—to assess their capability in synthesizing police facial portraits directly from text-based eyewitness descriptions.

---

### Key Technical Contributions & Features

1. **Text-to-Image & Image-to-Image Diffusion Exploration**:
   * Evaluates Latent Diffusion Models (Stable Diffusion v1.5/v2.1 & ControlNet) for synthesizing realistic facial images driven by text prompts.

2. **Morphofacial Parameter Conditioning**:
   * Analyzes how prompt engineering and structural ControlNet landmark masks can steer facial age, ethnicity, expression, and structural shape.

3. **Ethical, Bias & Legal Assessment**:
   * Highlights the inherent risks of GenAI in forensic contexts, including algorithmic bias, racial profiling, hallucination of non-existent facial features, and evidentiary inadmissibility.

---

### Critical Analysis & Comparison with ThirdEye v2

| Evaluation Dimension | GenAI Exploration (Sádaba-Campo et al., 2025) | ThirdEye v2 (Your Project) |
| --- | --- | --- |
| **Sketch Synthesis Engine** | Text-to-Image Latent Diffusion / ControlNet | Interactive Component-Based Composite Canvas |
| **Photorealism** | High (produces photo-like images) | Medium/High Line-Art & Feature Component Rendering |
| **Hallucination Risk** | Extremely High (AI invent details not stated by witness) | Zero (Deterministic rendering of witness selections) |
| **Court Admissibility** | Controversial (non-reproducible generative outputs) | Fully Admissible (exact audit log of selected components) |
| **System Footprint** | Massive GPU VRAM requirements (12GB+ VRAM) | Lightweight CPU/GPU JavaFX + FastAPI execution |
