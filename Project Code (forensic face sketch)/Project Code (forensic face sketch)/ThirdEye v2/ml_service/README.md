# ThirdEye ML Service (Python)

Deep-learning face matching backend for the ThirdEye JavaFX app.
Combines a pretrained **FaceNet** embedding with a shape-based **HOG**
descriptor (weighted 20/80) and ranks a dataset of suspect photos against a
composite sketch. The HOG term bridges the sketch↔photo domain gap.

---

## 1. Setup

### Prerequisites

- **Python 3.9+**
- Git (to clone the repo)

### Install dependencies

```bash
cd ml_service
pip install -r requirements.txt
```

> **Note:** `keras-facenet` pulls in TensorFlow (~500 MB). First model load
> downloads the pretrained weights (~90 MB).

> **Optional (recommended):** use a virtual environment so you don't pollute
> your global Python:
> ```bash
> cd ml_service
> python -m venv venv
> venv\Scripts\activate        # Windows
> # source venv/bin/activate   # macOS / Linux
> pip install -r requirements.txt
> ```

---

## 2. Get the dataset

The app matches sketches against a **gallery of suspect photos**. The app
expects them at `ml_service/dataset/gallery/`.

There are two ways to get the gallery photos:

### Option A — Use the CUFS / CUFSF evaluation dataset (recommended)

The evaluation dataset (~119 MB) is **not committed** to git to keep the
repository small. It is fetched on demand from Kaggle.

1. Create a free [Kaggle account](https://www.kaggle.com).
2. Create an API token:
   - Profile → Settings → **API** → *Create New Token*.
   - Save the downloaded `kaggle.json` and place it at:
     - `~/.kaggle/kaggle.json` (Windows: `C:\Users\<you>\.kaggle\kaggle.json`)
3. Download and unzip the dataset:
   ```bash
   cd ml_service
   python -m kaggle datasets download -d arbazkhan971/cuhk-face-sketch-database-cufs --unzip
   ```
   This creates `ml_service/dataset/` containing `photo/`, `photos/`,
   `cropped_sketch/`, `sketches/`, `photo_points/`, `sketch_points/`, etc.
4. Build the reproducible 100-pair test set:
   ```bash
   python prepare_dataset.py
   ```
   This matches photos and sketches by person ID and writes:
   - `dataset/gallery/` — 100 suspect **photos**
   - `dataset/queries/` — 100 corresponding **sketches**

   > **Important:** the raw Kaggle folders are **not paired by filename index** —
   > a naive `zip(photos, sketches)` gives meaningless accuracy. Always run
   > `prepare_dataset.py` so everyone measures the exact same set.

### Option B — Use your own suspect photos

Just drop any face photos (`.jpg`, `.jpeg`, `.png`) into `ml_service/dataset/gallery/`.
The service will scan them on the first match and cache embeddings.

---

## 3. Run the ML service

```bash
cd ml_service
python app.py
```

Or with uvicorn directly:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

Wait for the log line **`Model warmed up at startup.`** — the FaceNet model now
loads automatically when the service boots, so `/health` is immediately ready.

### Verify

```bash
# Service status — expect: {"status":"ok","model_loaded":true,...}
curl http://127.0.0.1:8000/health
```

> First boot can take a few minutes (TensorFlow import + weight download).
> If you see `model_loaded:false`, the model failed to load — check the
> terminal output for the error.

---

## 4. Using the API directly (optional, for testing)

```bash
# Embed a single photo
curl -X POST http://127.0.0.1:8000/embed -F "file=@C:/path/to/photo.jpg"

# Match a sketch against a folder of suspect photos
curl -X POST http://127.0.0.1:8000/match \
  -F "file=@C:/path/to/sketch.png" \
  -F "dataset_dir=C:/path/to/suspect_photos" \
  -F "top_n=10"
```

Embeddings are computed once and cached into `dataset_embeddings.npy` inside
the dataset folder. Subsequent `/match` calls are instant.

---

## 5. Run the Java app (end-to-end)

The app and the ML service must run **on the same machine** (the app reads the
photo paths the service returns).

1. Start the ML service (Section 3) and keep it running.
2. In a second terminal, from the project root:
   ```bash
   cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2"
   mvn clean javafx:run
   ```
3. Load/draw a sketch → click **▶ COMPARE**.
4. The app **auto-detects** `ml_service/dataset/gallery` and shows the top 10
   matches as photo thumbnails with similarity %.

---

## 6. Evaluating accuracy (rank metrics)

```bash
# Rank-1 / Rank-5 accuracy on the 100-pair set
python evaluate.py dataset/gallery dataset/queries 5

# Hybrid (FaceNet + HOG) evaluation
python hybrid_eval.py dataset/gallery dataset/queries
```

Measured sketch-to-photo accuracy on the 100-pair set:
**Hybrid (FaceNet 20% + HOG 80%) — 92% Rank-1** (98% Rank-3).
For reference, FaceNet alone scores 33% Rank-1; the shape-based HOG score is
what bridges the sketch↔photo domain gap. Weights are tunable via
`FACE_WEIGHT` in `app.py`.

### Precompute embeddings offline (optional)

```bash
python precompute.py C:/path/to/suspect_photos
```

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `MODULE_NOT_FOUND` / `pip install` fails | Install the missing package: `pip install <name>` from `requirements.txt`. |
| Kaggle download fails | Check `~/.kaggle/kaggle.json` exists with valid API token (Section 2). |
| `model_loaded:false` in `/health` | Model failed to load. Read the terminal error (usually a missing package or no network for the ~90 MB weights). |
| Port 8000 already in use | Another instance is already running. Stop it, or just use it. |
| App says "ML service is not running" | Start the service first (Section 3) and confirm `/health` returns `model_loaded:true`. |
| App shows empty images in results | The app reads photo paths from the service — both must run on the same machine, and the gallery must exist at `ml_service/dataset/gallery/`. |

---

## Java integration notes

The JavaFX app calls `/match` through the built-in JDK `java.net.http.HttpClient`
(no extra dependencies). The **COMPARE** button in `upload_sketch.fxml` runs a
dataset match against `ml_service/dataset/gallery` (auto-detected, no folder
picker) and shows the top 10 results as photo thumbnails with similarity %.

The app checks `/health` before matching and requires `model_loaded: true`.
The model loads **eagerly at startup** (see the `startup` event handler in
`app.py`), so teammates don't need to trigger a first request manually.

Default base URL: `http://127.0.0.1:8000` (change in `DeepMatchClient.java`).
