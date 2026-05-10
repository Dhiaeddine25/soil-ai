from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.results import ResultsSummaryResponse
from app.services.results_service import ResultsService


router = APIRouter(tags=["results"])


@router.get("/results/summary", response_model=ResultsSummaryResponse)
def results_summary(settings: Settings = Depends(get_settings)) -> ResultsSummaryResponse:
    service = ResultsService(settings)
    return service.get_summary()
