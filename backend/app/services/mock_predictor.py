from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from app.core.config import Settings
from app.schemas.prediction_quality import QualityCheck
from app.services.artifact_service import ArtifactService
from app.services.agronomic_advice_service import AgronomicAdviceService
from app.services.probability_calibration import ProbabilityCalibrationService
from app.services.prediction_decision_service import PredictionDecisionService
from app.services.interpretation_service import InterpretationService


NUTRIENT_LABELS = {
    "K": ["K0", "K1", "K2"],
    "N": ["N0", "N1", "N2"],
    "P": ["P0", "P1"],
}


@dataclass(frozen=True)
class MockPrediction:
    nutrient_levels: dict[str, str]
    confidences: dict[str, float]
    probability_map: dict[str, float]
    confidence: float


class MockPredictor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.artifacts = ArtifactService(settings)
        self.interpretation = InterpretationService()
        self.advice = AgronomicAdviceService()
        self.decision = PredictionDecisionService(settings)
        self.bundle = self.artifacts.load_bundle(settings.active_model_family, settings.active_model_dir)
        self.calibration = ProbabilityCalibrationService(
            settings,
            ProbabilityCalibrationService.build_entropy_profile(
                [self.bundle.directory],
                settings.calibration_entropy_fallback,
            ),
        )
        self.prediction_frame = (
            self.bundle.valid_predictions
            if self.bundle.valid_predictions is not None
            else self.bundle.test_predictions
        )

    def _signal_score(self, nutrient: str, probability_map: dict[str, float]) -> float:
        labels = NUTRIENT_LABELS[nutrient]
        desirability = {
            "K": [0.0, 0.5, 1.0],
            "N": [0.0, 0.5, 1.0],
            "P": [0.0, 1.0],
        }
        values = [max(float(probability_map.get(label, 0.0)), 0.0) for label in labels]
        total = sum(values)
        if total <= 0:
            return 0.0
        normalized = [value / total for value in values]
        return max(0.0, min(1.0, sum(weight * value for weight, value in zip(desirability[nutrient], normalized))))

    def _detail(
        self,
        nutrient: str,
        class_label: str,
        probability_map: dict[str, float],
        calibration_result=None,
    ) -> dict[str, object]:
        labels = NUTRIENT_LABELS[nutrient]
        raw_vector = calibration_result.raw_probabilities if calibration_result else [round(float(probability_map.get(label, 0.0)), 6) for label in labels]
        calibrated_vector = calibration_result.calibrated_probabilities if calibration_result else raw_vector
        confidence = max(calibrated_vector) if calibrated_vector else 0.0
        second_max = sorted(calibrated_vector, reverse=True)[1] if len(calibrated_vector) > 1 else 0.0
        raw_entropy = self.calibration._entropy(raw_vector)
        entropy = self.calibration._entropy(calibrated_vector)
        uncertainty_score = (second_max / confidence) if confidence > 0 else 1.0
        signal_score = self._signal_score(nutrient, probability_map)
        baseline = float(calibration_result.entropy_baseline) if calibration_result else self.settings.calibration_entropy_fallback
        ratio = float(calibration_result.entropy_ratio) if calibration_result else (entropy / baseline if baseline > 0 else 1.0)
        adjustment = float(calibration_result.uncertainty_adjustment) if calibration_result else 1.0
        uncertainty_score = max(0.0, min(1.0, uncertainty_score * adjustment))
        if confidence > 0.85 and entropy < 0.45 and uncertainty_score < 0.45:
            band = "état stable"
        elif confidence >= 0.5 and entropy >= 0.55:
            band = "zone incertaine"
        elif confidence < 0.5:
            band = "risque de déséquilibre"
        else:
            band = "lecture intermédiaire"
        return {
            "class": class_label,
            "confidence": round(confidence, 4),
            "probabilities": [round(float(value), 6) for value in calibrated_vector],
            "raw_probabilities": [round(float(value), 6) for value in raw_vector],
            "calibrated_probabilities": [round(float(value), 6) for value in calibrated_vector],
            "raw_entropy": round(float(raw_entropy), 4),
            "entropy": round(float(entropy), 4),
            "calibrated_entropy": round(float(entropy), 4),
            "entropy_baseline": round(baseline, 4),
            "entropy_ratio": round(ratio, 4),
            "calibration_factor": round(float(calibration_result.calibration_factor), 4) if calibration_result else round(self.settings.calibration_gamma, 4),
            "variance_index": round(max(confidence - second_max, 0.0), 4),
            "uncertainty_score": round(min(max(uncertainty_score, 0.0), 1.0), 4),
            "uncertainty_adjustment": round(adjustment, 4),
            "softened": bool(calibration_result.softened) if calibration_result else False,
            "signal_score": round(signal_score, 4),
            "interpretation": band,
        }

    def _soil_score_from_details(self, details: dict[str, dict[str, object]]) -> tuple[float, dict[str, object]]:
        k_max = float(details["potassium"]["confidence"])
        n_max = float(details["nitrogen"]["confidence"])
        p_max = float(details["phosphorus"]["confidence"])
        k_uncertainty = float(details["potassium"]["uncertainty_score"])
        n_uncertainty = float(details["nitrogen"]["uncertainty_score"])
        p_uncertainty = float(details["phosphorus"]["uncertainty_score"])
        max_mean = (k_max + n_max + p_max) / 3.0
        uncertainty_penalty = (k_uncertainty + n_uncertainty + p_uncertainty) / 3.0
        score = max(0.0, min(100.0, round((max_mean * 100.0) - (uncertainty_penalty * 10.0), 2)))
        return score, {
            "max_mean": round(max_mean, 4),
            "uncertainty_penalty": round(uncertainty_penalty, 4),
            "formula": "((K_max + N_max + P_max) / 3) * 100 - (uncertainty_penalty * 10)",
        }

    def _rng(self, image_name: str | None, parcel_id: str | None) -> random.Random:
        seed_source = (image_name or "") + "|" + (parcel_id or "")
        if not seed_source.strip("|"):
            return random.Random()
        seed_value = int(hashlib.sha256(seed_source.encode("utf-8")).hexdigest()[:16], 16)
        return random.Random(seed_value)

    def _row_to_prediction(self, row: pd.Series) -> MockPrediction:
        nutrient_levels: dict[str, str] = {}
        confidences: dict[str, float] = {}
        probabilities: dict[str, float] = {}

        for nutrient, labels in NUTRIENT_LABELS.items():
            candidates = []
            for label in labels:
                prob = float(row.get(f"{label}_prob", 0.0))
                candidates.append((label, prob))
                probabilities[label] = prob
            label, confidence = max(candidates, key=lambda item: item[1])
            nutrient_levels[nutrient] = label
            confidences[nutrient] = confidence

        confidence = sum(confidences.values()) / max(len(confidences), 1)
        confidence = min(max(confidence, self.settings.confidence_floor), 0.99)
        return MockPrediction(nutrient_levels, confidences, probabilities, confidence)

    def predict(self, image_name: str | None = None, parcel_id: str | None = None) -> dict:
        if self.prediction_frame is None or self.prediction_frame.empty:
            fallback = {"K_level": "K1", "N_level": "N1", "P_level": "P0"}
            confidence = 0.78
            interpretation = self.interpretation.build_interpretation(fallback, confidence)
            agronomic_advice = self.advice.build(fallback)
            nutrient_details = {
                "nitrogen": self._detail("N", fallback["N_level"], {}, None),
                "phosphorus": self._detail("P", fallback["P_level"], {}, None),
                "potassium": self._detail("K", fallback["K_level"], {}, None),
            }
            soil_health_score, score_breakdown = self._soil_score_from_details(nutrient_details)
            confidence_details = self.decision.build_confidence_details({})
            quality_check = QualityCheck(valid=True, status='ok')
            status = self.decision.determine_status(quality_check, confidence, confidence_details)
            return {
                "model_name": "SoilAI EfficientNetV2L",
                "prediction": fallback,
                **nutrient_details,
                "confidence": confidence,
                "status": status,
                "can_trust_result": self.decision.can_trust(status),
                "quality_check": quality_check,
                "confidence_details": confidence_details,
                "interpretation": interpretation,
                "recommendation": self.decision.recommendation_message(status),
                "agronomic_advice": agronomic_advice,
                "warning_message": self.decision.warning_message(status, quality_check),
                "recommendation_message": self.decision.recommendation_message(status),
                "is_mock": True,
                "timestamp": datetime.now(timezone.utc),
                "source": "fallback",
                "model_status": "mock",
                "probabilities": {},
                "soil_health_score": soil_health_score,
                "uncertainty_metrics": {},
                "debug": None,
                "score_breakdown": score_breakdown,
            }

        rng = self._rng(image_name, parcel_id)
        frame = self.prediction_frame.sample(n=1, random_state=rng.randint(0, 2**31 - 1))
        row = frame.iloc[0]
        mock = self._row_to_prediction(row)
        calibrated_probabilities, calibration_results = self.calibration.calibrate_probabilities(mock.probability_map)
        prediction = {
            "K_level": max(NUTRIENT_LABELS["K"], key=lambda label: calibrated_probabilities.get(label, 0.0)),
            "N_level": max(NUTRIENT_LABELS["N"], key=lambda label: calibrated_probabilities.get(label, 0.0)),
            "P_level": max(NUTRIENT_LABELS["P"], key=lambda label: calibrated_probabilities.get(label, 0.0)),
        }
        nitrogen_detail = self._detail("N", prediction["N_level"], mock.probability_map, calibration_results.get("N"))
        phosphorus_detail = self._detail("P", prediction["P_level"], mock.probability_map, calibration_results.get("P"))
        potassium_detail = self._detail("K", prediction["K_level"], mock.probability_map, calibration_results.get("K"))
        confidence = round(
            (float(nitrogen_detail["confidence"]) + float(phosphorus_detail["confidence"]) + float(potassium_detail["confidence"])) / 3.0,
            4,
        )
        interpretation = self.interpretation.build_interpretation(prediction, confidence)
        agronomic_advice = self.advice.build(prediction)
        confidence_details = self.decision.build_confidence_details(calibrated_probabilities)
        quality_check = QualityCheck(valid=True, status='ok')
        status = self.decision.determine_status(quality_check, confidence, confidence_details)
        return {
            "model_name": "SoilAI EfficientNetV2L",
            "prediction": prediction,
            "nitrogen": nitrogen_detail,
            "phosphorus": phosphorus_detail,
            "potassium": potassium_detail,
            "confidence": confidence,
            "status": status,
            "can_trust_result": self.decision.can_trust(status),
            "quality_check": quality_check,
            "confidence_details": confidence_details,
            "interpretation": interpretation,
            "recommendation": self.decision.recommendation_message(status),
            "agronomic_advice": agronomic_advice,
            "warning_message": self.decision.warning_message(status, quality_check),
            "recommendation_message": self.decision.recommendation_message(status),
            "is_mock": True,
            "timestamp": datetime.now(timezone.utc),
            "source": image_name or parcel_id or "sampled_prediction_row",
            "model_status": "mock",
            "probabilities": calibrated_probabilities,
            "soil_health_score": self._soil_score_from_details({
                "nitrogen": nitrogen_detail,
                "phosphorus": phosphorus_detail,
                "potassium": potassium_detail,
            })[0],
            "uncertainty_metrics": {
                "K": {k: v for k, v in potassium_detail.items() if k != "class"},
                "N": {k: v for k, v in nitrogen_detail.items() if k != "class"},
                "P": {k: v for k, v in phosphorus_detail.items() if k != "class"},
            },
            "debug": {
                "calibration_mode": "gamma",
                "calibration_factor": self.calibration._gamma(),
                "temperature_proxy": float(self.settings.calibration_temperature),
                "entropy_baseline": {nutrient: result.entropy_baseline for nutrient, result in calibration_results.items()},
                "raw_probabilities": mock.probability_map,
                "calibrated_probabilities": calibrated_probabilities,
                "entropy_before": {nutrient: result.raw_entropy for nutrient, result in calibration_results.items()},
                "entropy_after": {nutrient: result.calibrated_entropy for nutrient, result in calibration_results.items()},
                "uncertainty_adjustment": {nutrient: result.uncertainty_adjustment for nutrient, result in calibration_results.items()},
            } if self.settings.debug_predictions else None,
            "score_breakdown": self._soil_score_from_details({
                "nitrogen": nitrogen_detail,
                "phosphorus": phosphorus_detail,
                "potassium": potassium_detail,
            })[1],
        }
