#!/usr/bin/env python3
"""Compare two images by calling the prediction API and computing probabilistic similarity metrics.

Usage:
  python tools/compare_images.py imageA.jpg imageB.jpg [--url http://localhost:8000/predict] [--token <JWT>] [--out comparison_report.png]

This script:
- Posts both images to the prediction endpoint (multipart/form-data).
- Requests debug payload (adds query param debug=1 and header X-Debug-Predictions).
- Extracts raw/calibrated probabilities and entropies for N/P/K and a combined vector.
- Computes cosine similarity, KL divergence, Euclidean distance, entropy difference, confidence spread difference.
- Flags POSSIBLE OUTPUT COLLAPSE when thresholds are met.
- Optionally writes a matplotlib report image.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
except Exception:
    print("This script requires numpy. Install with: pip install numpy")
    raise

try:
    import requests
except Exception:
    print("This script requires requests. Install with: pip install requests")
    raise

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False


def post_image(url: str, path: str, token: Optional[str] = None) -> Dict[str, Any]:
    params = {"debug": "1"}
    headers = {"X-Debug-Predictions": "1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with open(path, "rb") as fh:
        files = {"file": (os.path.basename(path), fh, "image/jpeg")}
        resp = requests.post(url, params=params, files=files, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def safe_array(obj: Any) -> np.ndarray:
    if obj is None:
        return np.array([])
    if isinstance(obj, np.ndarray):
        return obj
    return np.array(obj, dtype=float)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return float('nan')
    if a.shape != b.shape:
        # try to align lengths by trimming to min length
        m = min(a.size, b.size)
        a = a.ravel()[:m]
        b = b.ravel()[:m]
    num = float(np.dot(a, b))
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    return num / den if den != 0 else float('nan')


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return float('nan')
    if a.shape != b.shape:
        m = min(a.size, b.size)
        a = a.ravel()[:m]
        b = b.ravel()[:m]
    return float(np.linalg.norm(a - b))


def kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    # KL(p || q)
    p = p.astype(float).ravel() + eps
    q = q.astype(float).ravel() + eps
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log(p / q)))


def entropy(vec: np.ndarray, eps: float = 1e-12) -> float:
    v = vec.astype(float).ravel() + eps
    v = v / v.sum()
    return float(-np.sum(v * np.log(v)))


def confidence_spread(vec: np.ndarray) -> float:
    # measure spread in confidence: standard deviation of probabilities
    v = vec.astype(float).ravel()
    return float(np.std(v))


def extract_nutrient_vectors(payload: Dict[str, Any], nutrient_key: str) -> Tuple[np.ndarray, np.ndarray, Optional[float], Optional[float]]:
    # Attempts to extract raw and calibrated probability vectors and entropies for a nutrient
    node = payload.get(nutrient_key) or payload.get(nutrient_key.lower())
    if not node or not isinstance(node, dict):
        return np.array([]), np.array([]), None, None
    raw = safe_array(node.get('raw_probabilities') or node.get('raw_probs') or node.get('raw'))
    calib = safe_array(node.get('calibrated_probabilities') or node.get('calibrated_probs') or node.get('calibrated'))
    e_before = node.get('raw_entropy') or node.get('entropy_before') or node.get('entropy')
    e_after = node.get('calibrated_entropy') or node.get('entropy_after')
    return raw, calib, e_before, e_after


def build_combined(vecs: List[np.ndarray]) -> np.ndarray:
    # concatenate calibrated vectors for combined analysis
    cleaned = [v.ravel() for v in vecs if v.size]
    if not cleaned:
        return np.array([])
    return np.concatenate(cleaned)


def human_list(vec: np.ndarray, topk: int = 5) -> str:
    if vec.size == 0:
        return '—'
    # show top-k indices and probabilities
    probs = vec.ravel()
    idx = np.argsort(-probs)[:topk]
    return ', '.join([f"#{i+1}:{probs[i]:.3f}" for i in idx])


def make_report(a_path: str, b_path: str, a_resp: Dict[str, Any], b_resp: Dict[str, Any], comparison: Dict[str, Any], out_path: Optional[str] = None) -> None:
    print('\n=== IMAGE A ===')
    print('file:', a_path)
    print('soil score:', a_resp.get('soil_health_score') or a_resp.get('score'))
    print('uncertainty:', a_resp.get('uncertainty_score') or a_resp.get('uncertainty'))
    print('nitrogen top:', human_list(np.array(a_resp.get('nitrogen', {}).get('calibrated_probabilities') if isinstance(a_resp.get('nitrogen'), dict) else [])))

    print('\n=== IMAGE B ===')
    print('file:', b_path)
    print('soil score:', b_resp.get('soil_health_score') or b_resp.get('score'))
    print('uncertainty:', b_resp.get('uncertainty_score') or b_resp.get('uncertainty'))
    print('nitrogen top:', human_list(np.array(b_resp.get('nitrogen', {}).get('calibrated_probabilities') if isinstance(b_resp.get('nitrogen'), dict) else [])))

    print('\n=== COMPARISON ===')
    print('cosine similarity (combined):', f"{comparison.get('combined', {}).get('cosine'):.4f}")
    print('KL divergence (combined):', f"{comparison.get('combined', {}).get('kl'):.4f}")
    print('euclidean (combined):', f"{comparison.get('combined', {}).get('euclidean'):.4f}")
    print('entropy delta (combined):', f"{comparison.get('combined', {}).get('entropy_delta'):.4f}")
    print('score delta:', float((a_resp.get('soil_health_score') or a_resp.get('score') or 0) - (b_resp.get('soil_health_score') or b_resp.get('score') or 0)))

    if comparison.get('collapse'):
        print('\n!! POSSIBLE OUTPUT COLLAPSE DETECTED !!')

    # plots
    if out_path and HAS_MATPLOTLIB:
        try:
            fig, axes = plt.subplots(3, 2, figsize=(10, 8))
            axes = axes.ravel()
            # N,P,K bars for both images (calibrated)
            keys = ['nitrogen', 'phosphorus', 'potassium']
            for i, key in enumerate(keys):
                a_vec = safe_array(a_resp.get(key, {}).get('calibrated_probabilities') if isinstance(a_resp.get(key), dict) else [])
                b_vec = safe_array(b_resp.get(key, {}).get('calibrated_probabilities') if isinstance(b_resp.get(key), dict) else [])
                if a_vec.size and b_vec.size and a_vec.size == b_vec.size:
                    ind = np.arange(a_vec.size)
                    width = 0.35
                    axes[i].bar(ind - width/2, a_vec, width, label='A')
                    axes[i].bar(ind + width/2, b_vec, width, label='B')
                    axes[i].set_title(key)
                    axes[i].legend()
            # entropy comparison
            axes[3].bar([0, 1], [comparison.get('nitrogen', {}).get('entropy_delta', 0), comparison.get('phosphorus', {}).get('entropy_delta', 0)])
            axes[3].set_title('Entropy Δ (N,P)')
            # similarity heatmap for per-nutrient cosine
            sim = [comparison.get('nitrogen', {}).get('cosine', 0), comparison.get('phosphorus', {}).get('cosine', 0), comparison.get('potassium', {}).get('cosine', 0)]
            axes[4].imshow(np.array(sim).reshape(1, -1), cmap='viridis', aspect='auto')
            axes[4].set_yticks([])
            axes[4].set_xticks([0,1,2])
            axes[4].set_xticklabels(['N','P','K'])
            axes[4].set_title('Per-nutrient similarity')
            # summary text
            axes[5].axis('off')
            axes[5].text(0, 0.5, json.dumps(comparison, indent=2), fontsize=6, family='monospace')
            plt.tight_layout()
            fig.savefig(out_path, dpi=150)
            print('\nSaved visualization to', out_path)
        except Exception as e:
            print('Failed to produce visualization:', e)
    elif out_path:
        print('Matplotlib not available; skipping visualization.')


def compare_payloads(a: Dict[str, Any], b: Dict[str, Any], thresholds: Dict[str, float]) -> Dict[str, Any]:
    nutrients = ['nitrogen', 'phosphorus', 'potassium']
    result: Dict[str, Any] = {}
    collapse = False

    per_nutrient = {}
    for n in nutrients:
        a_raw, a_calib, a_eb, a_ea = extract_nutrient_vectors(a, n)
        b_raw, b_calib, b_eb, b_ea = extract_nutrient_vectors(b, n)
        # fallback to probabilities map if nutrient node missing
        if a_calib.size == 0 and 'probabilities' in a:
            a_calib = safe_array(list(a.get('probabilities', {}).values()))
        if b_calib.size == 0 and 'probabilities' in b:
            b_calib = safe_array(list(b.get('probabilities', {}).values()))

        cos = cosine_similarity(a_calib, b_calib)
        kl = float('nan')
        try:
            kl = kl_divergence(a_calib, b_calib)
        except Exception:
            kl = float('nan')
        e_delta = (float(a_ea or 0) - float(b_ea or 0)) if (a_ea is not None or b_ea is not None) else float('nan')
        eu = euclidean_distance(a_calib, b_calib)
        spread_diff = abs(confidence_spread(a_calib) - confidence_spread(b_calib))

        per_nutrient[n] = {
            'cosine': cos,
            'kl': kl,
            'euclidean': eu,
            'entropy_delta': e_delta,
            'confidence_spread_diff': spread_diff,
        }
        # collapse heuristics per nutrient
        if not math.isnan(cos) and cos >= thresholds.get('cosine', 0.92):
            collapse = True
        if not math.isnan(eu) and eu <= thresholds.get('euclidean', 0.05):
            collapse = True
        if not math.isnan(e_delta) and abs(e_delta) <= thresholds.get('entropy_delta', 0.02):
            collapse = True

    # combined vector analysis
    a_vectors = [safe_array(a.get(n, {}).get('calibrated_probabilities') if isinstance(a.get(n), dict) else []) for n in nutrients]
    b_vectors = [safe_array(b.get(n, {}).get('calibrated_probabilities') if isinstance(b.get(n), dict) else []) for n in nutrients]
    a_comb = build_combined(a_vectors)
    b_comb = build_combined(b_vectors)
    combined = {
        'cosine': cosine_similarity(a_comb, b_comb),
        'kl': kl_divergence(a_comb, b_comb) if a_comb.size and b_comb.size else float('nan'),
        'euclidean': euclidean_distance(a_comb, b_comb),
        'entropy_delta': (entropy(a_comb) - entropy(b_comb)) if a_comb.size and b_comb.size else float('nan'),
    }

    if not math.isnan(combined['cosine']) and combined['cosine'] >= thresholds.get('cosine', 0.92):
        collapse = True
    if not math.isnan(combined['euclidean']) and combined['euclidean'] <= thresholds.get('euclidean', 0.05):
        collapse = True
    if not math.isnan(combined['entropy_delta']) and abs(combined['entropy_delta']) <= thresholds.get('entropy_delta', 0.02):
        collapse = True

    result.update(per_nutrient)
    result['combined'] = combined
    result['collapse'] = collapse
    return result


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description='Compare model predictions for two images')
    p.add_argument('image_a')
    p.add_argument('image_b')
    p.add_argument('--url', default=os.environ.get('PREDICT_URL', 'http://localhost:8000/predict'))
    p.add_argument('--token', default=os.environ.get('PREDICT_TOKEN'))
    p.add_argument('--out', default=os.environ.get('COMPARE_OUT', 'comparison_report.png'))
    p.add_argument('--no-plot', action='store_true')
    p.add_argument('--cosine-threshold', type=float, default=0.92)
    p.add_argument('--euclidean-threshold', type=float, default=0.05)
    p.add_argument('--entropy-threshold', type=float, default=0.02)
    args = p.parse_args(argv)

    # advise about debug env var: backend must be started with NPK_DEBUG_PREDICTIONS=true
    if 'NPK_DEBUG_PREDICTIONS' not in os.environ:
        os.environ['NPK_DEBUG_PREDICTIONS'] = '1'

    thresholds = {
        'cosine': args.cosine_threshold,
        'euclidean': args.euclidean_threshold,
        'entropy_delta': args.entropy_threshold,
    }

    a_resp = post_image(args.url, args.image_a, args.token)
    b_resp = post_image(args.url, args.image_b, args.token)

    comparison = compare_payloads(a_resp, b_resp, thresholds)

    out_path = args.out if not args.no_plot else None
    if out_path and not HAS_MATPLOTLIB:
        out_path = None

    make_report(args.image_a, args.image_b, a_resp, b_resp, comparison, out_path)

    return 0 if not comparison.get('collapse') else 2


if __name__ == '__main__':
    raise SystemExit(main())
