#!/usr/bin/env python3
"""Compare predictions on two images to confirm outputs are not constant."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def predict_image(image_path: Path) -> dict:
    from app.core.config import get_settings
    from app.services.ml_prediction_service import MLPredictionService

    settings = get_settings()
    service = MLPredictionService(settings)
    image_bytes = image_path.read_bytes()
    t0 = time.perf_counter()
    result = service.predict_npk(
        image_bytes=image_bytes,
        image_name=image_path.name,
        user_id="diagnostic",
    )
    elapsed = time.perf_counter() - t0
    prediction = result.get("prediction", {})
    return {
        "image": image_path.name,
        "elapsed": elapsed,
        "status": result.get("status"),
        "confidence": result.get("confidence"),
        "prediction": prediction,
        "refused": result.get("refused"),
        "refusal_reason": result.get("refusal_reason"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image1", type=Path)
    parser.add_argument("image2", type=Path)
    args = parser.parse_args()

    for image_path in (args.image1, args.image2):
        if not image_path.exists():
            raise FileNotFoundError(image_path)

    for payload in (predict_image(args.image1), predict_image(args.image2)):
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
