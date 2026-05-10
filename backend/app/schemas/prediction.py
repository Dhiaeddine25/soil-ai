from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.agronomic_advice import AgronomicAdvice
from app.schemas.prediction_quality import ConfidenceDetails, PredictionStatus, QualityCheck


class NutrientPrediction(BaseModel):
    K_level: str
    N_level: str
    P_level: str


class PredictionResponse(BaseModel):
    model_name: str
    prediction: NutrientPrediction | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    status: PredictionStatus
    can_trust_result: bool
    quality_check: QualityCheck
    confidence_details: ConfidenceDetails
    interpretation: str
    recommendation: str
    agronomic_advice: AgronomicAdvice | None = None
    warning_message: str
    recommendation_message: str
    is_mock: bool
    timestamp: datetime
    source: str
    model_status: str
    probabilities: dict[str, float] = Field(default_factory=dict)


class PredictMockRequest(BaseModel):
    image_name: str | None = None
    parcel_id: str | None = None
    user_id: str | None = None
