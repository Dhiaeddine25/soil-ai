from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PredictionStatus = Literal['image_non_exploitable', 'prediction_incertaine', 'confirmation_recommandee', 'ok']


class QualityCheck(BaseModel):
    valid: bool
    status: Literal['ok', 'image_non_exploitable']
    width: int | None = None
    height: int | None = None
    brightness: float | None = None
    contrast: float | None = None
    sharpness: float | None = None
    issues: list[str] = Field(default_factory=list)


class ConfidenceDetails(BaseModel):
    max_prob: float = Field(ge=0.0, le=1.0)
    second_prob: float = Field(ge=0.0, le=1.0)
    margin: float = Field(ge=0.0, le=1.0)
    top_label: str | None = None
    top_group: str | None = None
