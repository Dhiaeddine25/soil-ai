from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.parcel import ParcelPublic
from app.schemas.prediction import NutrientPrediction
from app.schemas.prediction import PredictionResponse


class HistoryEntry(BaseModel):
    id: str | None = None
    user_id: str
    parcel_id: str | None = None
    parcel: ParcelPublic | None = None
    image_name: str | None = None
    image_path: str | None = None
    image_url: str | None = None
    analysis_id: str
    created_at: datetime
    predictions: NutrientPrediction | None = None
    probabilities: dict[str, float] = Field(default_factory=dict)
    confidence: float = 0.0
    score: int = 0
    advice: str | None = None
    refused: bool = False
    refusal_reason: str | None = None
    prediction: PredictionResponse


class HistoryListResponse(BaseModel):
    user_id: str
    total: int
    entries: list[HistoryEntry] = Field(default_factory=list)
