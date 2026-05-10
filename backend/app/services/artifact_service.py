from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import Settings


LABELS = ["K0", "K1", "K2", "N0", "N1", "N2", "P0", "P1"]


@dataclass(frozen=True)
class ArtifactBundle:
    model_name: str
    family: str
    directory: Path
    valid_results: dict[str, Any]
    test_results: dict[str, Any]
    thresholds: dict[str, float]
    valid_predictions: pd.DataFrame | None
    test_predictions: pd.DataFrame | None


class ArtifactService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _read_csv(self, path: Path) -> pd.DataFrame | None:
        if not path.exists():
            return None
        return pd.read_csv(path)

    def load_bundle(self, family: str, directory: Path) -> ArtifactBundle:
        valid_results = self._read_json(directory / "results_valid.json")
        test_results = self._read_json(directory / "results_test.json")
        thresholds = self._load_thresholds(directory)
        valid_predictions = self._read_csv(directory / "valid_predictions.csv")
        test_predictions = self._read_csv(directory / "test_predictions.csv")
        return ArtifactBundle(
            model_name=f"npk_{family}",
            family=family,
            directory=directory,
            valid_results=valid_results,
            test_results=test_results,
            thresholds=thresholds,
            valid_predictions=valid_predictions,
            test_predictions=test_predictions,
        )

    def _load_thresholds(self, directory: Path) -> dict[str, float]:
        thresholds: dict[str, float] = {}
        for label in LABELS:
            path = directory / f"seuil_{label}.json"
            if not path.exists():
                continue
            payload = self._read_json(path)
            value = payload.get("seuil")
            if isinstance(value, (int, float)):
                thresholds[label] = float(value)
        return thresholds

    def build_model_summary(self, family: str, directory: Path, status: str) -> dict[str, Any]:
        bundle = self.load_bundle(family, directory)
        return {
            "model_name": f"SoilAI {family.replace('_', ' ').title()}",
            "family": family,
            "status": status,
            "version": "1.0.0",
            "description": self._describe_family(family),
            "image_size": 320 if family == self.settings.active_model_family else 224,
            "labels": LABELS,
            "performance": {
                "hamming_accuracy": bundle.valid_results.get("hamming_accuracy")
                or bundle.test_results.get("hamming_accuracy"),
                "macro_f1_global": bundle.valid_results.get("macro_f1_global")
                or bundle.test_results.get("macro_f1_global"),
                "per_label_accuracy": bundle.valid_results.get("per_label_accuracy")
                or bundle.test_results.get("per_label_accuracy", {}),
                "thresholds": bundle.valid_results.get("thresholds")
                or bundle.test_results.get("thresholds")
                or bundle.thresholds,
            },
            "artifact_paths": {
                "results_valid": str(directory / "results_valid.json"),
                "results_test": str(directory / "results_test.json"),
                "test_predictions": str(directory / "test_predictions.csv"),
                "valid_predictions": str(directory / "valid_predictions.csv"),
            },
        }

    def _describe_family(self, family: str) -> str:
        descriptions = {
            "efficientnetv2l": "Reference model family with the strongest validation results.",
            "densenet201": "Robust scientific baseline for comparison and explanation.",
            "mobilenetv2": "Lighter option useful for demos and constrained deployments.",
            "densenet": "Legacy training branch kept for project history and comparison.",
        }
        return descriptions.get(family, "Model available in the project artifacts.")
