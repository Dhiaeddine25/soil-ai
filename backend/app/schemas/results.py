from __future__ import annotations

from pydantic import BaseModel, Field


class ModelSummary(BaseModel):
    model_name: str
    family: str
    hamming_accuracy: float | None = None
    macro_f1_global: float | None = None
    per_label_accuracy: dict[str, float] = Field(default_factory=dict)
    thresholds: dict[str, float] = Field(default_factory=dict)
    sources: dict[str, str] = Field(default_factory=dict)


class ResultsSummaryResponse(BaseModel):
    best_model: ModelSummary
    models: list[ModelSummary]
    baseline_notes: list[str]
