from __future__ import annotations

from pathlib import Path


class ModelLoader:
    def __init__(self, model_dir: Path, image_size: int) -> None:
        self.model_dir = model_dir
        self.image_size = image_size

    def is_available(self) -> bool:
        expected = [self.model_dir / label / "model.keras" for label in ["K0", "K1", "K2", "N0", "N1", "N2", "P0", "P1"]]
        return all(path.exists() for path in expected)

    def load(self) -> object:
        raise NotImplementedError(
            "Real TensorFlow inference is prepared but not enabled yet. Wire the binary ensemble here when you want live predictions."
        )
