from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np

from app.core.config import Settings


NUTRIENT_LABELS: dict[str, list[str]] = {
    "K": ["K0", "K1", "K2"],
    "N": ["N0", "N1", "N2"],
    "P": ["P0", "P1"],
}


@dataclass(frozen=True)
class CalibrationResult:
    raw_probabilities: list[float]
    calibrated_probabilities: list[float]
    raw_entropy: float
    calibrated_entropy: float
    entropy_baseline: float
    entropy_ratio: float
    calibration_factor: float
    uncertainty_adjustment: float
    softened: bool


class ProbabilityCalibrationService:
    def __init__(self, settings: Settings, entropy_profile: Mapping[str, float] | None = None) -> None:
        self.settings = settings
        self.entropy_profile = dict(entropy_profile or {})

    @staticmethod
    def _entropy(values: list[float]) -> float:
        array = np.asarray(values, dtype=np.float32)
        if array.size == 0:
            return 0.0
        total = float(array.sum())
        if total <= 0:
            return 0.0
        normalized = array / total
        entropy = -float(np.sum(np.where(normalized > 0, normalized * np.log(normalized), 0.0)))
        if normalized.size <= 1:
            return 0.0
        return float(entropy / np.log(normalized.size))

    @staticmethod
    def build_entropy_profile(
        directories: list[Path],
        fallback_entropy: float,
    ) -> dict[str, float]:
        totals = {nutrient: 0.0 for nutrient in NUTRIENT_LABELS}
        counts = {nutrient: 0 for nutrient in NUTRIENT_LABELS}

        for directory in directories:
            for csv_name in ("valid_predictions.csv", "test_predictions.csv"):
                path = directory / csv_name
                if not path.exists():
                    continue
                try:
                    with path.open("r", encoding="utf-8", newline="") as handle:
                        reader = csv.DictReader(handle)
                        if not reader.fieldnames:
                            continue
                        for row in reader:
                            for nutrient, labels in NUTRIENT_LABELS.items():
                                vector = [float(row.get(f"{label}_prob", 0.0) or 0.0) for label in labels]
                                totals[nutrient] += ProbabilityCalibrationService._entropy(vector)
                                counts[nutrient] += 1
                except Exception:
                    continue

        return {
            nutrient: round(totals[nutrient] / counts[nutrient], 4) if counts[nutrient] else round(fallback_entropy, 4)
            for nutrient in NUTRIENT_LABELS
        }

    def calibrate_vector(self, nutrient: str, raw_values: list[float]) -> CalibrationResult:
        values = np.asarray([max(float(value), 0.0) for value in raw_values], dtype=np.float32)
        if values.size == 0:
            baseline = self._baseline_for(nutrient)
            return CalibrationResult([], [], 0.0, 0.0, baseline, 1.0, self._gamma(), 1.0, False)

        raw_entropy = self._entropy(values.tolist())
        total = float(values.sum())
        if total > 0:
            normalized = values / total
        else:
            normalized = np.full(values.shape, 1.0 / float(values.size), dtype=np.float32)

        gamma = self._gamma()
        calibrated = np.power(normalized, gamma)
        calibrated_total = float(calibrated.sum())
        if calibrated_total > 0:
            calibrated = calibrated / calibrated_total
        else:
            calibrated = np.full(normalized.shape, 1.0 / float(normalized.size), dtype=np.float32)

        softened = False
        max_prob = float(np.max(calibrated)) if calibrated.size else 0.0
        if max_prob > self.settings.calibration_soften_threshold:
            uniform = np.full(calibrated.shape, 1.0 / float(calibrated.size), dtype=np.float32)
            blend = min(
                0.25,
                self.settings.calibration_soften_strength + ((max_prob - self.settings.calibration_soften_threshold) * 0.5),
            )
            calibrated = (calibrated * (1.0 - blend)) + (uniform * blend)
            calibrated = calibrated / float(calibrated.sum())
            softened = True

        if calibrated.size > 1:
            second_best = float(np.partition(calibrated, -2)[-2])
            if second_best < self.settings.calibration_min_second_weight:
                floor = self.settings.calibration_min_second_weight
                calibrated = np.maximum(calibrated, floor)
                calibrated = calibrated / float(calibrated.sum())

        calibrated_entropy = self._entropy(calibrated.tolist())
        baseline = self._baseline_for(nutrient)
        entropy_ratio = (calibrated_entropy / baseline) if baseline > 0 else 1.0
        uncertainty_adjustment = 1.0 + ((entropy_ratio - 1.0) * self.settings.calibration_entropy_weight)
        uncertainty_adjustment = float(min(max(uncertainty_adjustment, 0.5), 1.5))

        return CalibrationResult(
            raw_probabilities=[round(float(value), 6) for value in values.tolist()],
            calibrated_probabilities=[round(float(value), 6) for value in calibrated.tolist()],
            raw_entropy=round(raw_entropy, 4),
            calibrated_entropy=round(calibrated_entropy, 4),
            entropy_baseline=round(baseline, 4),
            entropy_ratio=round(entropy_ratio, 4),
            calibration_factor=round(gamma, 4),
            uncertainty_adjustment=round(uncertainty_adjustment, 4),
            softened=softened,
        )

    def calibrate_probabilities(self, probabilities: Mapping[str, float]) -> tuple[dict[str, float], dict[str, CalibrationResult]]:
        calibrated: dict[str, float] = {}
        details: dict[str, CalibrationResult] = {}

        for nutrient, labels in NUTRIENT_LABELS.items():
            result = self.calibrate_vector(nutrient, [float(probabilities.get(label, 0.0)) for label in labels])
            details[nutrient] = result
            for label, calibrated_value in zip(labels, result.calibrated_probabilities):
                calibrated[label] = round(float(calibrated_value), 6)

        return calibrated, details

    def _baseline_for(self, nutrient: str) -> float:
        return float(self.entropy_profile.get(nutrient, self.settings.calibration_entropy_fallback))

    def _gamma(self) -> float:
        return float(min(max(self.settings.calibration_gamma, 0.7), 0.9))