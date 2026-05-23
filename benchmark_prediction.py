#!/usr/bin/env python3
"""Benchmark a local prediction path using a sample image from the repo."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _pick_sample_image() -> Path:
    candidates = [
        ROOT / "data" / "analysis_images",
        BACKEND_ROOT / "data" / "analysis_images",
    ]
    for folder in candidates:
        if folder.exists():
            for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.avif", "*.bmp"):
                items = sorted(folder.glob(pattern))
                if items:
                    return items[0]
    raise FileNotFoundError("No sample image found under data/analysis_images")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, help="Optional image to benchmark")
    parser.add_argument("--runs", type=int, default=3, help="Number of timed runs")
    args = parser.parse_args()

    from app.core.config import get_settings
    from app.services.ml_prediction_service import MLPredictionService, get_global_models

    image_path = args.image or _pick_sample_image()
    settings = get_settings()
    service = MLPredictionService(settings)
    image_bytes = image_path.read_bytes()

    t0 = time.perf_counter()
    models = get_global_models(settings)
    print(f"model_load={time.perf_counter() - t0:.3f}s families={sum(bool(v) for v in models.values())}")

    for index in range(args.runs):
        t0 = time.perf_counter()
        result = service.predict_npk(
            image_bytes=image_bytes,
            image_name=image_path.name,
            user_id="benchmark",
        )
        elapsed = time.perf_counter() - t0
        print(f"run={index + 1} total={elapsed:.3f}s status={result.get('status')} score={result.get('score')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
