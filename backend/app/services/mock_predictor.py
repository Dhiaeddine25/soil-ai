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
        self.prediction_frame = (
            self.bundle.valid_predictions
            if self.bundle.valid_predictions is not None
            else self.bundle.test_predictions
        )

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
            confidence_details = self.decision.build_confidence_details({})
            quality_check = QualityCheck(valid=True, status='ok')
            status = self.decision.determine_status(quality_check, confidence, confidence_details)
            return {
                "model_name": "SoilAI EfficientNetV2L",
                "prediction": fallback,
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
            }

        rng = self._rng(image_name, parcel_id)
        frame = self.prediction_frame.sample(n=1, random_state=rng.randint(0, 2**31 - 1))
        row = frame.iloc[0]
        mock = self._row_to_prediction(row)
        prediction = {
            "K_level": mock.nutrient_levels["K"],
            "N_level": mock.nutrient_levels["N"],
            "P_level": mock.nutrient_levels["P"],
        }
        interpretation = self.interpretation.build_interpretation(prediction, mock.confidence)
        agronomic_advice = self.advice.build(prediction)
        confidence_details = self.decision.build_confidence_details(mock.probability_map)
        quality_check = QualityCheck(valid=True, status='ok')
        status = self.decision.determine_status(quality_check, mock.confidence, confidence_details)
        return {
            "model_name": "SoilAI EfficientNetV2L",
            "prediction": prediction,
            "confidence": round(mock.confidence, 4),
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
            "probabilities": mock.probability_map,
        }
