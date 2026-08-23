"""
Third-Eye ML Evaluation Engine
Provides robust, reproducible evaluation metrics:
- Closed-set retrieval: Rank-1 to Rank-10, CMC curves
- Pairwise verification: Genuine vs Impostor score distributions, ROC-AUC, FAR, FRR, EER
- Identity-disjoint dataset splitting (Train / Val / Test)
"""
import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any

def to_pid(name: str) -> str:
    import re
    base = os.path.splitext(os.path.basename(name))[0]
    base = re.sub(r'-\d+$', '', base)
    base = base.replace('-01-sz1', '').replace('-01', '')
    return base

def build_identity_splits(
    gallery_files: List[str], 
    query_files: List[str], 
    seed: int = 42
) -> Dict[str, Any]:
    """Builds identity-disjoint Train (60), Validation (20), Test (rest) splits."""
    np.random.seed(seed)
    
    gal_map = {f: to_pid(f) for f in gallery_files}
    query_map = {f: to_pid(f) for f in query_files}
    
    unique_gal_pids = set(gal_map.values())
    unique_query_pids = set(query_map.values())
    
    paired_pids = sorted(list(unique_gal_pids.intersection(unique_query_pids)))
    distractor_pids = sorted(list(unique_gal_pids - unique_query_pids))
    
    shuffled_paired = paired_pids.copy()
    np.random.shuffle(shuffled_paired)
    
    train_pids = sorted(shuffled_paired[:60])
    val_pids = sorted(shuffled_paired[60:80])
    test_pids = sorted(shuffled_paired[80:])
    
    split_manifest = {
        "train_pids": train_pids,
        "val_pids": val_pids,
        "test_pids": test_pids,
        "distractor_pids": distractor_pids,
        "queries": {
            "train": [q for q in query_files if to_pid(q) in set(train_pids)],
            "val": [q for q in query_files if to_pid(q) in set(val_pids)],
            "test": [q for q in query_files if to_pid(q) in set(test_pids)]
        },
        "gallery": {
            "train": [g for g in gallery_files if to_pid(g) in set(train_pids)],
            "val": [g for g in gallery_files if to_pid(g) in set(val_pids)],
            "test": [g for g in gallery_files if to_pid(g) in set(test_pids) or to_pid(g) in set(distractor_pids)]
        }
    }
    return split_manifest

def evaluate_retrieval(
    similarity_matrix: np.ndarray,
    query_pids: List[str],
    gallery_pids: List[str],
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Computes CMC rank accuracy from a similarity matrix of shape (N_queries, N_gallery).
    """
    n_queries = len(query_pids)
    rank_hits = {k: 0 for k in range(1, top_k + 1)}
    reciprocal_ranks = []
    
    for i in range(n_queries):
        q_pid = query_pids[i]
        sims = similarity_matrix[i]
        sorted_indices = np.argsort(sims)[::-1]
        
        found_rank = None
        for rank_idx, g_idx in enumerate(sorted_indices, start=1):
            g_pid = gallery_pids[g_idx]
            if g_pid == q_pid:
                found_rank = rank_idx
                break
                
        if found_rank is not None:
            reciprocal_ranks.append(1.0 / found_rank)
            for k in range(found_rank, top_k + 1):
                rank_hits[k] += 1
        else:
            reciprocal_ranks.append(0.0)
            
    cmc_acc = {f"rank_{k}": float(rank_hits[k] / n_queries * 100.0) for k in range(1, top_k + 1)}
    mrr = float(np.mean(reciprocal_ranks))
    
    return {
        "num_queries": n_queries,
        "num_gallery": len(gallery_pids),
        "rank_acc": cmc_acc,
        "mrr": mrr
    }

def evaluate_verification(
    similarity_matrix: np.ndarray,
    query_pids: List[str],
    gallery_pids: List[str],
    num_thresholds: int = 1000
) -> Dict[str, Any]:
    """
    Computes ROC curve, AUC, FAR, FRR, EER and similarity score distributions.
    """
    genuine_scores = []
    impostor_scores = []
    
    for i, q_pid in enumerate(query_pids):
        for j, g_pid in enumerate(gallery_pids):
            score = similarity_matrix[i, j]
            if q_pid == g_pid:
                genuine_scores.append(score)
            else:
                impostor_scores.append(score)
                
    genuine_scores = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)
    
    if len(genuine_scores) == 0 or len(impostor_scores) == 0:
        return {"auc": 0.0, "eer": 0.0, "eer_threshold": 0.0}
        
    min_score = min(np.min(genuine_scores), np.min(impostor_scores))
    max_score = max(np.max(genuine_scores), np.max(impostor_scores))
    
    thresholds = np.linspace(min_score, max_score, num_thresholds)
    far_list, frr_list, tpr_list, fpr_list = [], [], [], []
    
    n_gen = len(genuine_scores)
    n_imp = len(impostor_scores)
    
    for t in thresholds:
        fa = np.sum(impostor_scores >= t)
        fr = np.sum(genuine_scores < t)
        
        far = fa / n_imp
        frr = fr / n_gen
        tpr = 1.0 - frr
        fpr = far
        
        far_list.append(far)
        frr_list.append(frr)
        tpr_list.append(tpr)
        fpr_list.append(fpr)
        
    far_arr = np.array(far_list)
    frr_arr = np.array(frr_list)
    
    eer_idx = np.argmin(np.abs(far_arr - frr_arr))
    eer = float((far_arr[eer_idx] + frr_arr[eer_idx]) / 2.0 * 100.0)
    eer_threshold = float(thresholds[eer_idx])
    
    sorted_idx = np.argsort(fpr_list)
    trapz_fn = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    if trapz_fn is None:
        raise AttributeError("Neither 'trapezoid' nor 'trapz' function found in numpy module")
    auc = float(trapz_fn(np.array(tpr_list)[sorted_idx], np.array(fpr_list)[sorted_idx]))
    
    return {
        "auc": auc,
        "eer": eer,
        "eer_threshold": eer_threshold,
        "genuine_mean": float(np.mean(genuine_scores)),
        "genuine_std": float(np.std(genuine_scores)),
        "impostor_mean": float(np.mean(impostor_scores)),
        "impostor_std": float(np.std(impostor_scores)),
        "genuine_scores": genuine_scores.tolist(),
        "impostor_scores": impostor_scores.tolist(),
        "thresholds": thresholds.tolist(),
        "far": far_list,
        "frr": frr_list,
        "tpr": tpr_list,
        "fpr": fpr_list
    }

def save_plots(
    verif_metrics: Dict[str, Any],
    cmc_metrics: Dict[str, Any],
    out_dir: str,
    prefix: str = "eval"
):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Plot CMC Curve
    ranks = list(range(1, len(cmc_metrics["rank_acc"]) + 1))
    accs = [cmc_metrics["rank_acc"][f"rank_{k}"] for k in ranks]
    
    plt.figure(figsize=(8, 5))
    plt.plot(ranks, accs, 'o-', color='#1a73e8', linewidth=2, label='Hybrid System')
    plt.title(f'Cumulative Match Characteristic (CMC) Curve - {prefix}')
    plt.xlabel('Rank')
    plt.ylabel('Identification Accuracy (%)')
    plt.xticks(ranks)
    plt.ylim(0, 105)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'{prefix}_cmc.png'), dpi=300)
    plt.close()
    
    # 2. Plot ROC Curve
    if "fpr" in verif_metrics and "tpr" in verif_metrics:
        plt.figure(figsize=(7, 6))
        plt.plot(verif_metrics["fpr"], verif_metrics["tpr"], color='#34a853', linewidth=2,
                 label=f'ROC (AUC = {verif_metrics["auc"]:.4f})')
        plt.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random Chance')
        plt.title(f'Receiver Operating Characteristic (ROC) - {prefix}')
        plt.xlabel('False Positive Rate (FAR)')
        plt.ylabel('True Positive Rate (1 - FRR)')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'{prefix}_roc.png'), dpi=300)
        plt.close()
        
    # 3. Plot Score Distributions
    if "genuine_scores" in verif_metrics and "impostor_scores" in verif_metrics:
        plt.figure(figsize=(8, 5))
        plt.hist(verif_metrics["genuine_scores"], bins=40, alpha=0.6, color='#1a73e8', density=True, label='Genuine Pairs')
        plt.hist(verif_metrics["impostor_scores"], bins=40, alpha=0.6, color='#ea4335', density=True, label='Impostor Pairs')
        plt.axvline(verif_metrics["eer_threshold"], color='black', linestyle=':', label=f'EER Threshold ({verif_metrics["eer_threshold"]:.3f})')
        plt.title(f'Similarity Score Distribution - {prefix}')
        plt.xlabel('Hybrid Cosine Similarity')
        plt.ylabel('Density')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'{prefix}_score_dist.png'), dpi=300)
        plt.close()
