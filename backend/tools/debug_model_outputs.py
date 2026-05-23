#!/usr/bin/env python3
"""Print raw outputs for each model on two images and compare them.

Use this to confirm whether the model weights themselves are changing with the image.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings
from app.services.ml_prediction_service import _artifact_path


def _prepare(path: Path) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    image = image.resize((224, 224))
    img_array = np.array(image).astype("float32") / 255.0
    print("IMAGE SIZE:", image.size)
    print("IMAGE MODE:", image.mode)
    print("IMAGE ARRAY MEAN:", float(np.mean(img_array)))
    print("IMAGE ARRAY STD:", float(np.std(img_array)))
    print("SHAPE BEFORE EXPAND:", img_array.shape)
    img_array = np.expand_dims(img_array, axis=0)
    print("FINAL SHAPE:", img_array.shape)
    return img_array


def _load_and_predict(model_path: Path, batch: np.ndarray) -> list[float]:
    import tensorflow as tf

    model = tf.keras.models.load_model(str(model_path), compile=False)
    print("Loaded model:", model_path)
    raw = model(batch, training=False)
    raw_list = np.asarray(raw).ravel().tolist()
    print("RAW PREDICTION:", raw_list)
    return raw_list


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image1", type=Path)
    parser.add_argument("image2", type=Path)
    args = parser.parse_args()

    settings = get_settings()
    families = ["npk_models_efficientnetv2l", "npk_models_mobilenetv2", "npk_models_densenet201"]

    for image_path in (args.image1, args.image2):
        print("=== IMAGE ===", image_path.name)
        batch = _prepare(image_path)
        for family in families:
            print("=== FAMILY ===", family)
            for label in ["K0", "K1", "K2", "N0", "N1", "N2", "P0", "P1"]:
                model_path = _artifact_path(settings.root_dir / family, label)
                if model_path is None:
                    print("Missing model:", family, label)
                    continue
                pred = _load_and_predict(model_path, batch)
                print(f"{family}/{label} -> {pred}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())