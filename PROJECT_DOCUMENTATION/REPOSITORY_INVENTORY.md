# REPOSITORY INVENTORY

**Repository Path**: `c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye`  
**Inventory Date**: August 23, 2026  
**Auditor**: Automated Forensic Audit Suite  

---

## 1. Directory & File Classification Table

| Path | Type | Purpose | Runtime Role | Status |
| :--- | :--- | :--- | :--- | :--- |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/ThirdEyeV2.java` | Java Source | Desktop Client Entry Point | Primary UI Launcher | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/DashboardController.java` | Java Source | Interactive Sketch Builder Canvas Controller | Primary UI Canvas Manager | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/Upload_sketchController.java` | Java Source | Match Submission & Result Thumbnail Display | Primary Matching UI Controller | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/DeepMatchClient.java` | Java Source | HTTP REST Client for Python ML Microservice | Network Bridge | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/SuspectDatabase.java` | Java Source | DAO for `suspects.db` SQLite Database | Database Data Access Object | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/connectdb.java` | Java Source | JDBC Handler for `login.sqlite` | Database Connection Handler | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/pom.xml` | Maven XML | JavaFX 21 Build Configuration | Authoritative Java Build System | ACTIVE / BUILD |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/build.xml` | Ant XML | Legacy NetBeans Ant Build Script | Obsolete Build System | LEGACY / BUILD |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/app.py` | Python Source | FastAPI ML Microservice REST API | Primary ML Inference Microservice | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/requirements.txt` | Text Manifest | Python Service Dependencies | Environment Specification | ACTIVE / BUILD |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/evaluate.py` | Python Source | Single-stream FaceNet Evaluator | Evaluation Tool | EXPERIMENTAL |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/hybrid_eval.py` | Python Source | Dual-stream Hybrid Evaluator (100-pair) | Evaluation Tool | EXPERIMENTAL |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/evaluation_engine.py` | Python Source | Metrics Engine (Rank-N, EER, AUC, ROC) | Metric Computation Library | ACTIVE |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/run_tests.py` | Python Source | Unit & Integration Test Suite | Automated Test Suite | TEST |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/split_manifest.json` | JSON Data | Identity Split Definition (60 train / 20 val / 21 test) | Dataset Protocol Definition | ACTIVE / DATA |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/FINAL_CANONICAL_METRICS.json` | JSON Data | Authoritative Single Source of Truth Metrics | Benchmark Metric Manifest | ACTIVE / DATA |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/experiments/exp05_cross_modal/best_cross_modal_model.weights.h5` | Binary Model | Keras Weights for Projection Head (164k params) | Model Artifact | ACTIVE / MODEL |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye_FaceMatch/` | Directory | Legacy Java Swing + AWS Rekognition App | Superseded Project | LEGACY |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/Java Libraies(Part 1)/` | Directory | Legacy JAR Dependencies (`sqlite-jdbc-3.30.1.jar`, etc.) | Archived Libraries | LEGACY |
| `Third-Eye-Final-Year-Project/` | Directory | Report PDFs, Logos, Screenshots, Published Paper | Project Documentation & Media | DOCUMENTATION |
