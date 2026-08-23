# REPOSITORY CLEANUP INVENTORY

**Audit Date**: August 23, 2026  
**Auditor**: Senior Software Architect & Repository Maintainer  

---

## 1. Directory & Artifact Forensic Classification Table

| Path | Category | Purpose | Runtime Required? | Git Track? | Action | Evidence / Rationale |
| :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/` | **PRODUCTION** | Main JavaFX Desktop UI & Controllers | **YES** | **YES** | **KEEP** | Core JavaFX frontend codebase. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/` | **PRODUCTION** | FastAPI ML Microservice REST backend | **YES** | **YES** | **KEEP** | Core Python ML matching engine. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/pom.xml` | **PRODUCTION** | Maven 21 dependency configuration | **YES** | **YES** | **KEEP** | Authoritative Java build definition. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/experiments/` | **ML EXPERIMENT** | empirical research tracks `exp01` .. `exp08` | NO | **YES** | **KEEP** | Essential research reproducibility lineage. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/aws-java-sdk-1.11.777.jar` | **DEAD / POLLUTION** | 155.43 MB AWS SDK JAR left in source tree | NO | NO | **DELETE** | ThirdEye v2 does not use AWS; managed by Maven. Caused past Git push failure. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/sketch elements/element softcopy.psd` | **THIRD-PARTY / DESIGN** | 91.14 MB Photoshop source asset file | NO | NO | **MOVE / IGNORE** | Source design file; not used by runtime JavaFX app. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/sqlite-jdbc-3.30.1.jar` | **DEAD / POLLUTION** | 5.81 MB duplicate JAR in src tree | NO | NO | **DELETE** | Duplicate; Maven manages `sqlite-jdbc-3.42.0.0` in `pom.xml`. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/activation.jar` | **DEAD / POLLUTION** | 0.12 MB duplicate JAR in src tree | NO | NO | **DELETE** | Duplicate; managed via Maven. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/mail-1.4.7.jar` | **DEAD / POLLUTION** | 0.50 MB duplicate JAR in src tree | NO | NO | **DELETE** | Duplicate; managed via Maven. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/lib/` | **LEGACY / POLLUTION** | Duplicate JAR directory (`sqlite`, `mail`, `activation`) | NO | NO | **DELETE** | Obsolete pre-Maven JAR folder. |
| `Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye_FaceMatch/` | **LEGACY** | Superseded Java Swing AWS Rekognition app | NO | **YES** | **ARCHIVE** | Historical prototype; kept in repo with clear legacy warning. |
| `Third-Eye-Final-Year-Project/` | **DOCUMENTATION / MEDIA** | Screenshots, logo, and published research PDF links | NO | **YES** | **KEEP** | Valuable presentation & thesis media. |
