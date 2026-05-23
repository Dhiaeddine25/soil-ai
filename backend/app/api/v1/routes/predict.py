from __future__ import annotations

import logging
import time
from fastapi import APIRouter, Depends, File, Form, Header, UploadFile, HTTPException

from app.deps import get_current_user
from app.core.config import Settings, get_settings
from app.models.user import User
from app.schemas.prediction import PredictionResponse
from app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["prediction"])


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
    print("PIPELINE STEP: ROUTER")
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
        print("PIPELINE STEP: SERVICE")
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
    print("PIPELINE STEP: RESPONSE")
    logger.info(
        "[Predict/Real] RESPONSE SENT request_id=%s, analysis_id=%s, status=%s, elapsed=%.2fs",
        request_id,
        result.analysis_id,
        result.status,
        elapsed,
    )
    return result