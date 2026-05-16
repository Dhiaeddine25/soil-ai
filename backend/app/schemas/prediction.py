from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agronomic_advice import AgronomicAdvice
from app.schemas.prediction_quality import ConfidenceDetails, PredictionStatus, QualityCheck


class NutrientPrediction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    K_level: str = Field(alias="K", serialization_alias="K_level")
    N_level: str = Field(alias="N", serialization_alias="N_level")
    P_level: str = Field(alias="P", serialization_alias="P_level")


class PredictionResponse(BaseModel):
    analysis_id: str | None = None
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
    field_advice: str | None = None
    field_disclaimer: str | None = None
    score: int | None = None
    refused: bool = False
    refusal_reason: str | None = None
    image_name: str | None = None
    image_url: str | None = None
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
