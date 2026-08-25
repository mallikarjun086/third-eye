# IIIT-D SKETCH DATABASE — PASSWORD REQUIRED NOTICE

**Archive File Located**: `C:\Users\Mallikarjun Gala\OneDrive\Desktop\IIITD_SketchDatabase.zip`  
**Archive File Size**: 717.7 MB (752,581,894 bytes)  
**Status**: `BLOCKED — IIIT-D ARCHIVE PASSWORD REQUIRED`  

---

## Technical Details

The physical archive file `IIITD_SketchDatabase.zip` was discovered on the local system. Upon attempting automated extraction, the Python `zipfile` engine reported:

```text
RuntimeError: File 'IIITD_SketchDatabase/Forensic sketch database/Forensic_sketches.txt' is encrypted, password required for extraction
```

## Mandatory Access Step for User

To extract and integrate this dataset into ThirdEye v2:

1. Obtain the official decryption password via IIIT-Delhi's Image Processing and Computer Vision Lab (IPAG) dataset agreement.
2. Provide the password or extract `IIITD_SketchDatabase.zip` directly into `data/iiitd/`.
3. Re-run `python scripts/verify_physical_datasets.py` to auto-parse and manifest the 542 physical images.
