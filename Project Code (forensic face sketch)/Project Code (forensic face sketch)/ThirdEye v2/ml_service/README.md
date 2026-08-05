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

### Precompute embeddings offline (optional)

```bash
python precompute.py C:/path/to/suspect_photos
```

## Java integration

The JavaFX app calls `/match` through the built-in JDK `java.net.http.HttpClient`
(no extra dependencies). When the Python service is **not running**, the app
falls back to the existing pure-Java comparison, so nothing breaks.

Default base URL: `http://127.0.0.1:8000` (change in `DeepMatchClient.java`).
