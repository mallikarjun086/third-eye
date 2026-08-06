# Third-Eye — Forensic Face Sketch Recognition System

Third-Eye matches a composite (drawn) sketch against a gallery of suspect photos
and returns a ranked list of matches with similarity percentages. It combines a
**JavaFX desktop app** with a **Python deep-learning service** (FaceNet + HOG).

## Project layout

```
ThirdEye v2/
├── src/thirdeye/v2/        JavaFX app (Java 21, Maven)
│   ├── upload_sketch.fxml  Sketch + single COMPARE button screen
│   └── DeepMatchClient.java  Talks to the Python service over HTTP
├── pom.xml                 Maven build (JavaFX 21)
└── ml_service/             Python FastAPI + FaceNet backend
    ├── app.py              The matching service (runs on port 8000)
    ├── dataset/gallery/    Suspect photos used for matching (100 photos)
    └── dataset/queries/    Sketches used to evaluate accuracy
```

## Prerequisites

- **Java 21** (e.g. Temurin/Adoptium JDK 21)
- **Maven** 3.9+
- **Python 3.9+** with the packages in `ml_service/requirements.txt`

## How to run (Windows)

The app needs the Python ML service running first. Open **two terminals**.

### 1. Start the ML service

```bash
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service"
python app.py
```

Wait for the log line `Model warmed up at startup.` (first run may take a few
minutes — it downloads ~90 MB of FaceNet weights). Confirm it's ready:

```
curl http://127.0.0.1:8000/health
```

You should see `"status":"ok","model_loaded":true`.

> The model now loads automatically at startup. If you see `model_loaded:false`,
> the service is still loading or failed — check the terminal for errors.

### 2. Run the JavaFX app

Open a **second** terminal (keep the ML service running):

```bash
cd "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2"
mvn clean javafx:run
```

> If Maven uses the wrong JDK, point it at Java 21 first:
> ```bash
> $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot"
> $env:Path = "$env:JAVA_HOME\bin;$env:Path"
> ```

## Using the app

1. **Load / draw a sketch** in the app (composite sketch screen).
2. Click **▶ COMPARE**.
3. The app **auto-detects** `ml_service/dataset/gallery` — no folder picker.
4. A popup shows the **top 10 ranked matches as photo thumbnails**, each with
   its rank, file name, and color-coded similarity % (green ≥90, blue ≥75,
   yellow ≥60, red <60).

## If something fails

| Symptom | Fix |
|---|---|
| "ML service is not running" | The Python service isn't up, or `/health` showed `model_loaded:false`. Start it, wait for `Model warmed up at startup.` |
| Port 8000 already in use | Another instance is running. Stop it first, or just use the one already running. |
| Folder picker appears on COMPARE | `ml_service/dataset/gallery` was not found. Run the app from inside the `ThirdEye v2` folder, or restore the dataset. |
| Empty match images | The photo paths returned by the service don't exist locally — both app and service must run on the same machine. |

## Evaluation / dataset notes

The evaluation dataset (CUFS/CUFSF, ~119 MB) is **not committed** to git. See
[`ml_service/README.md`](Project%20Code%20(forensic%20face%20sketch)/Project%20Code%20(forensic%20face%20sketch)/ThirdEye%20v2/ml_service/README.md)
for how to download it with Kaggle and reproduce the 100-pair test set.

Measured sketch-to-photo accuracy: **Hybrid (FaceNet 20% + HOG 80%) = 92%
Rank-1** (98% Rank-3) on the 100-pair set.
