#!/usr/bin/env python3
"""Convert Keras models to TensorFlow Lite for faster CPU inference.

Default mode uses float16 quantization, which is the safest drop-in option for
most SavedModel / Keras pipelines. Use --quantization dynamic for a smaller
model with no representative dataset.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def convert_model(model_path: Path, output_path: Path, quantization: str) -> None:
    import tensorflow as tf

    model = tf.keras.models.load_model(model_path, compile=False)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    if quantization == "float16":
        converter.target_spec.supported_types = [tf.float16]
    elif quantization == "dynamic":
        pass
    else:
        raise ValueError(f"Unsupported quantization mode: {quantization}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(converter.convert())


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Keras model files to TFLite.")
    parser.add_argument("--input", required=True, type=Path, help="Path to model.keras or model.h5")
    parser.add_argument("--output", required=True, type=Path, help="Destination .tflite file")
    parser.add_argument(
        "--quantization",
        default="float16",
        choices=("float16", "dynamic"),
        help="Quantization mode to use",
    )
    args = parser.parse_args()

    convert_model(args.input, args.output, args.quantization)
    print(f"Converted {args.input} -> {args.output} ({args.quantization})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
