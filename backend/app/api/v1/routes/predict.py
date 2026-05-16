from __future__ import annotations

import logging
import time
from fastapi import APIRouter, Depends, File, Form, Header, UploadFile, HTTPException

from app.deps import get_current_user
from app.core.config import Settings, get_settings
from app.models.user import User
from app.schemas.prediction import NutrientPrediction, PredictMockRequest, PredictionResponse
from app.services.agronomic_advice_service import AgronomicAdviceService
from app.services.history_service import HistoryService
from app.services.mock_predictor import MockPredictor
from app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["prediction"])


@router.post("/predict/mock", response_model=PredictionResponse)
def predict_mock(
    request: PredictMockRequest,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> PredictionResponse:
    t0 = time.monotonic()
    logger.info(
        "[Predict/Mock] Requête reçue - image=%s, parcel=%s, user=%s",
        request.image_name,
        request.parcel_id,
        current_user.id,
    )

    predictor = MockPredictor(settings)
    payload = predictor.predict(image_name=request.image_name, parcel_id=request.parcel_id)
    advice_service = AgronomicAdviceService()
    active_user_id = current_user.id
    payload["source"] = f"mock:{active_user_id}"
    payload["agronomic_advice"] = payload.get("agronomic_advice") or advice_service.build(
        NutrientPrediction(**payload["prediction"])
    )
    previous_entry = (
        HistoryService(settings)
        .list_entries(active_user_id, parcel_id=request.parcel_id)
        .entries[:1]
    )
    previous_prediction = previous_entry[0].prediction.prediction if previous_entry else None
    previous_advice = previous_entry[0].prediction.agronomic_advice if previous_entry else None
    field_advice, field_disclaimer = advice_service.build_field_advice(
        payload["agronomic_advice"],
        payload["confidence"],
        previous_prediction=previous_prediction,
        previous_advice=previous_advice,
    )
    payload["field_advice"] = field_advice
    payload["field_disclaimer"] = field_disclaimer
    prediction = PredictionResponse(**payload)
    HistoryService(settings).add_entry(
        user_id=active_user_id,
        prediction=prediction,
        parcel_id=request.parcel_id,
        image_name=request.image_name,
    )
    elapsed = time.monotonic() - t0
    logger.info("[Predict/Mock] Terminé en %.2fs - status=%s", elapsed, prediction.status)
    return prediction


@router.post("/predict", response_model=PredictionResponse)
async def predict_real(
    image: UploadFile = File(...),
    parcel_id: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> PredictionResponse:
    """
    Real soil-image NPK prediction.

    Pipeline:
    - REQUEST RECEIVED
    - AUTH OK (via dependency)
    - IMAGE RECEIVED
    - PREPROCESS START
    - MODEL LOAD START (from cache)
    - MODEL LOAD END
    - PREDICTION START
    - PREDICTION END
    - DB SAVE START
    - DB SAVE END
    - RESPONSE SENT
    """
    t0 = time.monotonic()
    request_id = x_request_id or "no-x-request-id"
    logger.info(
        "[Predict/Real] REQUEST RECEIVED request_id=%s, user=%s, image=%s, parcel=%s, content_type=%s",
        request_id,
        current_user.id,
        image.filename,
        parcel_id,
        image.content_type,
    )

    service = PredictionService(settings)

    try:
        logger.info("[Predict/Real] AUTH OK user=%s", current_user.id)
        result = await service.predict(image=image, parcel_id=parcel_id, user_id=current_user.id)
    except HTTPException:
        raise
    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.error(
            "[Predict/Real] UNHANDLED ERROR after %.2fs request_id=%s: %s",
            elapsed,
            request_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "prediction_failed",
                "message": f"Erreur interne après {elapsed:.1f}s: {str(exc)}",
                "request_id": request_id,
            },
        ) from exc

    elapsed = time.monotonic() - t0
    logger.info(
        "[Predict/Real] RESPONSE SENT request_id=%s, analysis_id=%s, status=%s, elapsed=%.2fs",
        request_id,
        result.analysis_id,
        result.status,
        elapsed,
    )
    return result