from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ModelPerformance(BaseModel):
    hamming_accuracy: float | None = None
    macro_f1_global: float | None = None
    per_label_accuracy: dict[str, float] = Field(default_factory=dict)
    thresholds: dict[str, float] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    model_name: str
    family: str
    status: str
    version: str = "1.0.0"
    description: str
    image_size: int
    labels: list[str]
    performance: ModelPerformance = Field(default_factory=ModelPerformance)
    artifact_paths: dict[str, str] = Field(default_factory=dict)


class ModelsInfoResponse(BaseModel):
    active_model: ModelInfo
    available_models: list[ModelInfo]
    server_time: datetime
    note: str
