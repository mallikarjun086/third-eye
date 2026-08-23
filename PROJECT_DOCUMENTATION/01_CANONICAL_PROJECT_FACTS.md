# 01 — CANONICAL PROJECT FACTS

* **PROJECT TITLE**: AI-Based Forensic Face Sketch and Recognition System  
* **SYSTEM CODE NAME**: `ThirdEye v2`  
* **PRIMARY BENCHMARK ACCURACY**: **85.71% Rank-1** (18/21 test queries vs full 189 gallery, AUC = **0.9898**)  
* **SECONDARY TEST POOL ACCURACY**: **90.48% Rank-1** (19/21 test queries vs 109 test pool gallery, AUC = **0.9914**)  
* **100-PAIR SUBSET ACCURACY**: **92.00% Rank-1** (92/100 queries matched)  
* **RAW FACENET ACCURACY**: **12.11% Rank-1** (23/190 queries matched across full dataset)  
* **WARM INFERENCE LATENCY**: **307.90 ms median** (328.64 ms mean across 30 runs)  
* **PROJECTION HEAD PARAMETERS**: **164,736 trainable parameters** (`Dense(256) -> BN -> ReLU -> Dropout(0.2) -> Dense(128) -> L2_Normalize`)  
* **PRODUCTION HOG DIMENSION**: **3,600 dimensions** ($20 \times 20$ cells $\times 9$ bins)  
* **PRODUCTION FUSION WEIGHT**: $\alpha^* = 0.05$ ($S = 0.05 S_{\text{deep}} + 0.95 S_{\text{hog}}$)  
