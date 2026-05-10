from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.model_info import ModelInfo, ModelsInfoResponse
from app.services.model_registry import ModelRegistry


router = APIRouter(tags=["models"])


@router.get("/models/info", response_model=ModelsInfoResponse)
def models_info(settings: Settings = Depends(get_settings)) -> ModelsInfoResponse:
    registry = ModelRegistry(settings)
    payload = registry.get_registry()
    active = ModelInfo(**payload["active_model"])
    available = [ModelInfo(**item) for item in payload["available_models"]]
    return ModelsInfoResponse(
        active_model=active,
        available_models=available,
        server_time=datetime.now(timezone.utc),
        note=payload["note"],
    )
