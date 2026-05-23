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


class NutrientPredictionDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    predicted_class: str = Field(alias="class", serialization_alias="class")
    confidence: float
    probabilities: list[float]
    raw_probabilities: list[float] | None = None
    calibrated_probabilities: list[float] | None = None
    interpretation: str
    signal_score: float = Field(ge=0.0, le=1.0)
    raw_entropy: float | None = None
    calibrated_entropy: float | None = None
    entropy_baseline: float | None = None
    entropy_ratio: float | None = None
    calibration_factor: float | None = None
    uncertainty_adjustment: float | None = None
    softened: bool | None = None


class ImageQualityMetadata(BaseModel):
    image_quality_score: float | None = None
    warning: str | None = None
    recommendations: list[str] = Field(default_factory=list)


class PredictionResponse(BaseModel):
    analysis_id: str | None = None
    model_name: str
    npk_prediction: NutrientPrediction | None = None
    prediction: NutrientPrediction | None = None
    nitrogen: NutrientPredictionDetail | None = None
    phosphorus: NutrientPredictionDetail | None = None
    potassium: NutrientPredictionDetail | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: PredictionStatus
    can_trust_result: bool
    quality_check: QualityCheck
    confidence_details: ConfidenceDetails | None
    interpretation: str
    recommendation: str
    agronomic_advice: AgronomicAdvice | None = None
    field_advice: str | None = None
    field_disclaimer: str | None = None
    soil_health_score: float | None = None
    image_quality: ImageQualityMetadata | None = None
    uncertainty_metrics: dict[str, dict[str, object]] = Field(default_factory=dict)
    debug: dict[str, object] | None = None
    score_breakdown: dict[str, object] | None = None
    score: int | None = None
    refused: bool = False
    refusal_reason: str | None = None
    image_name: str | None = None
    image_url: str | None = None
    warning_message: str
    recommendation_message: str
    warning: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    image_quality_score: float | None = None
    is_mock: bool
    timestamp: datetime
    source: str
    model_status: str
    probabilities: dict[str, float] = Field(default_factory=dict)


class PredictMockRequest(BaseModel):
    image_name: str | None = None
    parcel_id: str | None = None
    user_id: str | None = None
