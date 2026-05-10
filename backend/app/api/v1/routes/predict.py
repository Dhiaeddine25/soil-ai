from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile

from app.deps import get_current_user
from app.core.config import Settings, get_settings
from app.models.user import User
from app.schemas.prediction import PredictMockRequest, PredictionResponse
from app.services.history_service import HistoryService
from app.services.mock_predictor import MockPredictor
from app.services.prediction_service import PredictionService


router = APIRouter(tags=["prediction"])


@router.post("/predict/mock", response_model=PredictionResponse)
def predict_mock(
    request: PredictMockRequest,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> PredictionResponse:
    predictor = MockPredictor(settings)
    payload = predictor.predict(image_name=request.image_name, parcel_id=request.parcel_id)
    active_user_id = current_user.id
    payload["source"] = f"mock:{active_user_id}"
    prediction = PredictionResponse(**payload)
    HistoryService(settings).add_entry(
        user_id=active_user_id,
        prediction=prediction,
        parcel_id=request.parcel_id,
        image_name=request.image_name,
    )
    return prediction


@router.post("/predict", response_model=PredictionResponse)
async def predict_real(
    image: UploadFile = File(...),
    parcel_id: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> PredictionResponse:
    service = PredictionService(settings)
    return await service.predict(image=image, parcel_id=parcel_id, user_id=current_user.id)
