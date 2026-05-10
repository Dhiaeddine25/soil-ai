from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.parcel import ParcelPublic
from app.schemas.prediction import PredictionResponse


class HistoryEntry(BaseModel):
    user_id: str
    parcel_id: str | None = None
    parcel: ParcelPublic | None = None
    image_name: str | None = None
    analysis_id: str
    created_at: datetime
    prediction: PredictionResponse


class HistoryListResponse(BaseModel):
    user_id: str
    total: int
    entries: list[HistoryEntry] = Field(default_factory=list)
