from __future__ import annotations

import asyncio
import logging
import os
import time

from fastapi.concurrency import run_in_threadpool
from fastapi import UploadFile

from app.core.config import Settings
from app.schemas.prediction import PredictionResponse
from app.services.history_service import HistoryService
from app.services.ml_prediction_service import MLPredictionService

logger = logging.getLogger(__name__)

PREDICTION_TIMEOUT_SECONDS = float(os.environ.get("PREDICTION_TIMEOUT_SECONDS", "120"))


class PredictionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ml = MLPredictionService(settings)

    async def predict(
        self,
        image:      UploadFile,
        parcel_id:  str | None = None,
        user_id:    str = "guest",
    ) -> PredictionResponse:
        """Run prediction in a thread pool; time each sub-phase individually."""
        t_start     = time.monotonic()
        request_ms  = time.monotonic()
        print("PIPELINE STEP: SERVICE")

        image_bytes = await image.read()
        logger.info(
            "[Predict] image_read  bytes=%d  name=%s  %.3fs",
            len(image_bytes), image.filename, time.monotonic() - request_ms,
        )

        try:
            ml_start   = time.monotonic()
            payload    = await asyncio.wait_for(
                run_in_threadpool(
                    self.ml.predict_npk,
                    image_bytes=image_bytes,
                    image_name=image.filename,
                    parcel_id=parcel_id,
                    user_id=user_id,
                ),
                timeout=PREDICTION_TIMEOUT_SECONDS,
            )
            logger.info(
                "[Predict] ml_predict done  %.3fs  analysis_id=%s  status=%s",
                time.monotonic() - ml_start,
                payload.get("analysis_id"),
                payload.get("status"),
            )
        except asyncio.TimeoutError as exc:
            elapsed = time.monotonic() - t_start
            logger.error(
                "[Predict] ml_predict TIMEOUT after %.3fs (limit=%.1fs)",
                elapsed,
                PREDICTION_TIMEOUT_SECONDS,
                exc_info=True,
            )
            from fastapi import HTTPException

            raise HTTPException(
                status_code=504,
                detail={
                    "error": "prediction_timeout",
                    "message": f"La prédiction a dépassé {PREDICTION_TIMEOUT_SECONDS:.0f}s.",
                },
            ) from exc
        except Exception as exc:
            elapsed = time.monotonic() - t_start
            logger.error("[Predict] ml_predict FAILED after %.3fs : %s", elapsed, exc, exc_info=True)
            raise

        # ── Pydantic validation ─────────────────────────────────────────────
        try:
            prediction = PredictionResponse.model_validate(payload)
        except Exception as exc:
            logger.error("[Predict] pydantic_validation FAILED: %s\npayload=%s", exc, payload)
            raise

        print("PIPELINE STEP: RESPONSE")

        # ── DB persist (run in threadpool to avoid blocking async loop) ─────
        def _persist_history():
            logger.info("[Predict] DB SAVE START user=%s analysis_id=%s", user_id, prediction.analysis_id)
            history = HistoryService(self.settings)
            history._run_migrations()
            history.add_entry(
                user_id       = user_id,
                prediction    = prediction,
                parcel_id     = parcel_id,
                image_name    = image.filename,
                image_url     = getattr(prediction, "image_url", None),
                image_path    = payload.get("image_path"),
                analysis_id   = prediction.analysis_id,
            )
            logger.info("[Predict] DB SAVE END")

        try:
            t0 = time.monotonic()
            await run_in_threadpool(_persist_history)
            logger.info("[Predict] db_save %.3fs", time.monotonic() - t0)
        except Exception as exc:
            # Prediction succeeded; do not fail the HTTP request on DB errors
            logger.error("[Predict] db_save ERROR: %s", exc, exc_info=True)

        elapsed_total = time.monotonic() - t_start
        logger.info(
            "[Predict] ← done  total=%.3fs  analysis_id=%s  status=%s",
            elapsed_total, prediction.analysis_id, prediction.status,
        )
        return prediction
