from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.history import router as history_router
from app.api.v1.routes.parcels import router as parcels_router
from app.api.v1.routes.models import router as models_router
from app.api.v1.routes.predict import router as predict_router
from app.api.v1.routes.results import router as results_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(history_router)
api_router.include_router(parcels_router)
api_router.include_router(models_router)
api_router.include_router(predict_router)
api_router.include_router(results_router)
