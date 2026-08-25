# REPOSITORY POLLUTION AUDIT

**Audit Date**: August 23, 2026  
**Focus**: Identification of unneeded binaries, oversize source artifacts, duplicate dependencies, and build clutter.

---

## 1. Oversize Binary Artifacts Audit

| Path | Size (MB) | Purpose / Origin | Production Status | Git Status | Recommendation |
| :--- | :---: | :--- | :---: | :---: | :--- |
| `src/thirdeye/v2/elements/aws-java-sdk-1.11.777.jar` | **155.43 MB** | Legacy AWS SDK JAR accidentally committed inside source assets tree | **UNUSED** | Tracked | **DELETE FROM SRC TREE** (Causes Git push failure; ThirdEye v2 uses local FastAPI microservice, not AWS). |
| `src/thirdeye/v2/elements/sketch elements/element softcopy.psd` | **91.14 MB** | Photoshop source canvas design asset | **UNUSED BY RUNTIME** | Tracked | **MOVE TO ARCHIVE / IGNORE** (Source graphic file; not loaded by JavaFX). |
| `src/thirdeye/v2/elements/sqlite-jdbc-3.30.1.jar` | **5.81 MB** | Legacy pre-Maven JDBC driver JAR | **SUPERSEDED** | Tracked | **DELETE** (Maven `pom.xml` manages `sqlite-jdbc-3.42.0.0` automatically). |
| `src/thirdeye/v2/elements/mail-1.4.7.jar` | **0.50 MB** | Legacy pre-Maven JavaMail JAR | **SUPERSEDED** | Tracked | **DELETE** (Managed via Maven `pom.xml`). |
| `src/thirdeye/v2/elements/activation.jar` | **0.12 MB** | Legacy pre-Maven Activation JAR | **SUPERSEDED** | Tracked | **DELETE** (Managed via Maven `pom.xml`). |
| `ThirdEye v2/lib/` (3 JARs) | **6.43 MB** | Duplicate `lib/` directory | **SUPERSEDED** | Tracked | **DELETE** (Obsolete folder; Maven downloads dependencies directly). |

---

## 2. Total Space Reclaimed

* **Total Binary Pollution Identified**: **~259.43 MB**
* **Impact**: Removing these unneeded binary files resolves the 100 MB GitHub file size limit issue and reduces repo size by **over 90%**.
