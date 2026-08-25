# VIVA DEFENSE & EXAMINATION GUIDE: THIRDEYE V2

**Project Title**: AI-Based Forensic Face Sketch and Recognition System  
**System Code Name**: `ThirdEye v2`  

---

## 1. Project Summaries for Examiners

### A. 30-Second Explanation

> "ThirdEye v2 is an AI-assisted forensic workstation that allows law enforcement officers to build composite face sketches from eyewitness descriptions using an interactive JavaFX GUI, and instantly match those sketches against a mugshot database. Matching is powered by a Python/FastAPI microservice running a hybrid ML model—combining a metric-learned FaceNet projection head with spatial CLAHE HOG descriptors—achieving an 85.71% Rank-1 sketch-to-photo matching accuracy across a 189-candidate gallery and 90.48% on the test pool benchmark."

### B. 1-Minute Explanation

> "In forensic investigations, matching hand-drawn or composite sketches against photo databases is challenging because standard deep learning models trained on RGB photos fail on line drawings due to the cross-modal domain gap. ThirdEye v2 solves this with a two-part architecture: first, a desktop JavaFX GUI where non-artist officers assemble sketches by selecting and manipulating layered facial elements. Second, a FastAPI machine learning microservice that receives the sketch and runs a dual-stream feature extraction engine. One stream passes a 512-d FaceNet embedding through a trained 2-layer MLP projection head to align sketch and photo spaces; the second stream extracts spatial CLAHE HOG descriptors. By fusing these scores, ThirdEye v2 achieves 85.71% Rank-1 accuracy on the full 189-candidate gallery (AUC = 0.9898), compared to just 12.11% for raw FaceNet."

### C. 3-Minute Explanation

> "Our project addresses the critical law enforcement challenge of identifying unknown suspects from eyewitness testimony. The system consists of two tightly integrated components: a JavaFX desktop front-end and a Python/FastAPI ML microservice.
>
> On the front-end, `DashboardController.java` provides a multi-layer canvas where users can select transparent PNG elements for hair, eyes, eyebrows, nose, mouth, chin, and facial hair, scaling and positioning them dynamically to create a composite sketch.
>
> When the officer clicks 'Compare', `DeepMatchClient.java` sends the composited sketch via HTTP multipart POST to our microservice `app.py`. The microservice executes a hybrid recognition pipeline to overcome the cross-modal domain gap:
>
> 1. Deep Feature Stream: Extracts a 512-d FaceNet embedding and projects it into a 128-d space using a custom MLP trained with Triplet Margin Loss on sketch-photo pairs.
> 2. Spatial Contour Stream: Preprocesses the image with CLAHE and extracts an 11,552-d (or 3,600-d in production) Histogram of Oriented Gradients (HOG) weighted by an elliptical facial feature mask.
> 3. Late Score Fusion: Computes cosine similarity for both streams and combines them using optimal weighting ($\alpha^*=0.05$ in production; $\alpha=0.20$ in standard test protocols), yielding an 85.71% Rank-1 accuracy on the full 189-candidate gallery and 90.48% on the test pool benchmark, compared to just 12.11% for raw FaceNet.
"

---

## 2. Step-by-Step Execution Trace

```text

1. User launches JavaFX App (ThirdEyeV2.java)
   ├── SQLite database connection initialized (connectdb.java -> suspects.db)
   └── UI displays Login / Dashboard Screen

2. User builds Composite Sketch (DashboardController.java)
   ├── User clicks facial category buttons (Hair, Eyes, Nose, Lips, etc.)
   ├── System loads PNG assets from src/thirdeye/v2/elements/
   ├── User adjusts image positioning / scale / layering on Canvas
   └── User clicks "Save & Compare"

3. Canvas Rendering & Network Transmission
   ├── DashboardController exports Canvas node to PNG byte array
   └── Upload_sketchController calls DeepMatchClient.match(sketchFile, datasetDir, topN)
       └── Constructs HTTP multipart POST payload to http://127.0.0.1:8000/match

4. FastAPI Microservice Execution (ml_service/app.py)
   ├── Router receives multipart request containing sketch bytes & gallery path
   ├── Service checks cached embeddings in dataset_embeddings.npy (or computes if missing)
   ├── Stream A: FaceNet extracts 512d vector -> Projection Head transforms to 128d
   ├── Stream B: Image converted to Grayscale -> CLAHE applied -> 3,600d HOG vector extracted
   ├── Scores computed against all gallery photos: S_hybrid = 0.05*S_deep + 0.95*S_hog
   └── Microservice returns JSON array of Top-10 suspects with similarity percentages

5. UI Result Visualization (Upload_sketchController.java)
   └── JavaFX populates grid view with suspect mugshots, names, ages, and similarity badges.
```

---

## 3. Key Viva Questions & Answers

1. **Q: What is the primary architecture of ThirdEye v2?**  
   *A:* A hybrid client-server microservice architecture consisting of a JavaFX desktop GUI for user interaction and a Python FastAPI REST service for ML inference.
2. **Q: Why did you separate the UI (Java) from the ML engine (Python)?**  
   *A:* JavaFX provides responsive desktop graphics rendering, while Python is the standard ecosystem for machine learning libraries (TensorFlow, OpenCV, NumPy).
3. **Q: What is the cross-modal domain gap in face recognition?**  
   *A:* The discrepancy in feature representation between line-drawn sketches (lacking color/texture) and photorealistic RGB photos.
4. **Q: Why does standard FaceNet fail on sketches, and how much does ThirdEye v2 improve accuracy?**  
   *A:* FaceNet's early convolutional layers look for rich RGB color distributions and skin textures, which do not exist in black-and-white line sketches. Raw FaceNet achieves only **12.11% Rank-1 accuracy**. By adding our custom **2-layer MLP Projection Head** and **Spatially-Weighted CLAHE HOG Fusion Engine**, ThirdEye v2 boosts accuracy by **+73.6 percentage points**, reaching up to **92.00% Rank-1 accuracy**:

   | Model Configuration | Evaluation Protocol / Gallery | Rank-1 Accuracy | Rank-5 Accuracy | AUC Score | Accuracy Improvement |
   | :--- | :--- | :---: | :---: | :---: | :---: |
   | **Raw FaceNet Baseline** | Full CUFS (190 Queries / 189 Gallery) | **12.11%** | 22.11% | 0.8124 | *Baseline* |
   | **Raw FaceNet Baseline** | 100-Pair Subset | **33.00%** | 52.00% | 0.8910 | *Subset Baseline* |
   | **ThirdEye v2 Hybrid Engine** | Primary Held-Out Test Set (189 Gallery) | **85.71%** | **95.24%** | **0.9898** | **+73.60%** |
   | **ThirdEye v2 Hybrid Engine** | Secondary Test Pool (109 Gallery) | **90.48%** | **95.24%** | **0.9914** | **+78.37%** |
   | **ThirdEye v2 Hybrid Engine** | 100-Pair Evaluation Subset | **92.00%** | **98.00%** | **0.9942** | **+59.00%** |

5. **Q: How does the Projection Head solve this gap?**  
   *A:* It is a 2-Dense-layer MLP trained with Triplet Margin Loss ($\text{margin}=0.3$) that maps both sketch and photo embeddings into a shared 128-d space where matching identities are close together.
6. **Q: What is the purpose of HOG in your system?**  
   *A:* HOG captures structural shape and edge orientation invariants that remain consistent between a sketch and a photo regardless of color.
7. **Q: Why use CLAHE before computing HOG?**  
   *A:* CLAHE (Contrast Limited Adaptive Histogram Equalization) normalizes local contrast, making line-stroke intensities uniform.
8. **Q: What is late score fusion?**  
   *A:* Combining the similarity scores of two independent classifiers (Deep Embedding + Spatial HOG) at the output stage using a weighted formula.
9. **Q: What is the production fusion weight $\alpha$?**  
   *A:* $\alpha^* = 0.05$ (5% Deep Embedding + 95% Spatial HOG), determined via grid search in `exp06_fusion.py` and set in `app.py`.
10. **Q: What Rank-1 accuracy did your hybrid model achieve?**  
    *A:* **85.71% Rank-1 accuracy** on the primary held-out 189-candidate gallery (AUC = 0.9898), **90.48%** on the 109-candidate test pool protocol, and **92.00%** on the 100-pair subset.
