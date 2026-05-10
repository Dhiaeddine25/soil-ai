from __future__ import annotations

from io import BytesIO

from PIL import UnidentifiedImageError
from fastapi import UploadFile

from app.core.config import Settings
from app.ml.loader import ModelLoader
from app.schemas.prediction import NutrientPrediction, PredictionResponse
from app.schemas.prediction_quality import ConfidenceDetails, QualityCheck
from app.services.agronomic_advice_service import AgronomicAdviceService
from app.services.image_quality_service import ImageQualityService
from app.services.history_service import HistoryService
from app.services.prediction_decision_service import PredictionDecisionService
from app.services.mock_predictor import MockPredictor


class PredictionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mock_predictor = MockPredictor(settings)
        self.loader = ModelLoader(settings.active_model_dir, settings.image_size)
        self.history = HistoryService(settings)
        self.image_quality = ImageQualityService(settings)
        self.decision = PredictionDecisionService(settings)
        self.advice = AgronomicAdviceService()

    async def predict(self, image: UploadFile, parcel_id: str | None = None, user_id: str = "guest") -> PredictionResponse:
        image_bytes = await image.read()
        quality_check = self.image_quality.analyze(image_bytes)

        if not quality_check.valid:
            status = 'image_non_exploitable'
            confidence_details = ConfidenceDetails(max_prob=0.0, second_prob=0.0, margin=0.0, top_label=None, top_group=None)
            payload = {
                "model_name": "SoilAI EfficientNetV2L",
                "prediction": None,
                "confidence": 0.0,
                "status": status,
                "can_trust_result": False,
                "quality_check": quality_check,
                "confidence_details": confidence_details,
                "interpretation": "L’image ne permet pas une lecture NPK fiable.",
                "recommendation": self.decision.recommendation_message(status),
                "agronomic_advice": None,
                "warning_message": self.decision.warning_message(status, quality_check),
                "recommendation_message": self.decision.recommendation_message(status),
                "is_mock": True,
                "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
                "source": f"uploaded_image:{user_id}",
                "model_status": "rejected",
                "probabilities": {},
            }
            prediction = PredictionResponse(**payload)
            self.history.add_entry(user_id=user_id, prediction=prediction, parcel_id=parcel_id, image_name=image.filename)
            return prediction

        if self.loader.is_available():
            try:
                self.loader.load()
            except NotImplementedError:
                payload = self.mock_predictor.predict(image_name=image.filename, parcel_id=parcel_id)
                payload["model_status"] = "prepared"
                payload["is_mock"] = True
                payload["source"] = f"uploaded_image:{user_id}"
                payload["quality_check"] = quality_check
                payload["confidence_details"] = self.decision.build_confidence_details(payload.get("probabilities", {}))
                payload["status"] = self.decision.determine_status(quality_check, payload["confidence"], payload["confidence_details"])
                payload["can_trust_result"] = self.decision.can_trust(payload["status"])
                payload["warning_message"] = self.decision.warning_message(payload["status"], quality_check)
                payload["recommendation_message"] = self.decision.recommendation_message(payload["status"])
                payload["recommendation"] = payload["recommendation_message"]
                payload["prediction"] = payload.get("prediction")
                payload["agronomic_advice"] = payload.get("agronomic_advice") or self.advice.build(NutrientPrediction(**payload["prediction"]))
                prediction = PredictionResponse(**payload)
                self.history.add_entry(user_id=user_id, prediction=prediction, parcel_id=parcel_id, image_name=image.filename)
                return prediction

        payload = self.mock_predictor.predict(image_name=image.filename, parcel_id=parcel_id)
        payload["model_status"] = "mock"
        payload["is_mock"] = True
        payload["source"] = f"uploaded_image:{user_id}"
        payload["quality_check"] = quality_check
        payload["confidence_details"] = self.decision.build_confidence_details(payload.get("probabilities", {}))
        payload["status"] = self.decision.determine_status(quality_check, payload["confidence"], payload["confidence_details"])
        payload["can_trust_result"] = self.decision.can_trust(payload["status"])
        payload["warning_message"] = self.decision.warning_message(payload["status"], quality_check)
        payload["recommendation_message"] = self.decision.recommendation_message(payload["status"])
        payload["recommendation"] = payload["recommendation_message"]
        payload["agronomic_advice"] = payload.get("agronomic_advice") or self.advice.build(NutrientPrediction(**payload["prediction"]))
        prediction = PredictionResponse(**payload)
        self.history.add_entry(user_id=user_id, prediction=prediction, parcel_id=parcel_id, image_name=image.filename)
        return prediction
