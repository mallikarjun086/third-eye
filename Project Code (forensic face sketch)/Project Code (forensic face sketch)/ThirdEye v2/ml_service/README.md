# ThirdEye ML Service (Python)

Deep-learning face matching backend for the ThirdEye JavaFX app.
Uses a pretrained **FaceNet** model to embed faces and ranks a dataset of
suspect photos against a composite sketch via cosine similarity.

## Setup

Requires Python 3.9+.

```bash
cd ml_service
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

> **Note:** `keras-facenet` pulls in TensorFlow (~500 MB). First model load
> downloads the pretrained weights (~90 MB).

## Run

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

Or run the module directly:

```bash
python app.py
```

## Verify

```bash
# Service status
curl http://127.0.0.1:8000/health

# Quick test — embed a single photo
curl -X POST http://127.0.0.1:8000/embed -F "file=@C:/path/to/photo.jpg"
```

## Dataset (CUFS / CUFSF)

The evaluation dataset (~119 MB) is **not committed** to git to keep the
repository small. It is fetched on demand from Kaggle. You need a free Kaggle
account and a token in `~/.kaggle/access_token`.

```bash
python -m kaggle datasets download -d arbazkhan971/cuhk-face-sketch-database-cufs --unzip
```

Unzip the archive into `ml_service/dataset/` so it contains `photo/`,
`photos/`, `cropped_sketch/`, `sketches/`, `photo_points/`, `sketch_points/`,
etc.

> **Note:** the raw photo/sketch folders in this Kaggle copy are **not paired by
> filename index**. Build a correctly-paired gallery + query set from the
> overlapping person IDs before evaluating:

```python
import os, shutil
base = "dataset"
p = {os.path.splitext(f)[0].replace("-01", ""): f for f in os.listdir(f"{base}/photos")}
s = {os.path.splitext(f)[0].replace("-01-sz1", ""): f for f in os.listdir(f"{base}/sketches")}
os.makedirs(f"{base}/gallery", exist_ok=True)
os.makedirs(f"{base}/queries", exist_ok=True)
for pid in set(p) & set(s):
    shutil.copy(f"{base}/photos/{p[pid]}", f"{base}/gallery/{pid}.jpg")
    shutil.copy(f"{base}/sketches/{s[pid]}", f"{base}/queries/{pid}.jpg")
```

This produces a 100-pair test set (photo in `gallery/`, sketch in `queries/`).
Measured sketch-to-photo Rank-1 accuracy on this set: **33%**.

## Dataset comparison

Point the service at a folder of suspect photos:

```bash
curl -X POST http://127.0.0.1:8000/match \
  -F "file=@C:/path/to/sketch.png" \
  -F "dataset_dir=C:/path/to/suspect_photos" \
  -F "top_n=10"
```

Embeddings are computed once and cached into `dataset_embeddings.npy` inside
the dataset folder. Subsequent `/match` calls are instant.

Evaluate rank accuracy on a gallery/query pair (100-pair set):

```bash
python evaluate.py dataset/gallery dataset/queries 5
```

### Precompute embeddings offline (optional)

```bash
python precompute.py C:/path/to/suspect_photos
```

## Java integration

The JavaFX app calls `/match` through the built-in JDK `java.net.http.HttpClient`
(no extra dependencies). When the Python service is **not running**, the app
falls back to the existing pure-Java comparison, so nothing breaks.

Default base URL: `http://127.0.0.1:8000` (change in `DeepMatchClient.java`).
