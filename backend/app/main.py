from __future__ import annotations

import logging
import os
import time

# Set TensorFlow process env before importing services that import TF.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.db.init_db import init_db
from app.services.ml_prediction_service import get_global_models, reset_global_models

# ── Timeout middleware ─────────────────────────────────────────────────────────
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "120"))  # seconds

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import asyncio
        try:
            return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT)
        except asyncio.TimeoutError:
            return Response(
                content=f'{{"detail": "Request timeout after {REQUEST_TIMEOUT}s"}}',
                status_code=504,
                media_type="application/json"
            )

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.api_version,
    description=(
        "FastAPI backend for SoilAI / Webbeck: NPK pre-diagnostic from soil images, "
        "with a realistic mock mode based on the project's training artifacts."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TimeoutMiddleware)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Backend Webbeck API is running",
        "docs":    "/docs",
        "health":  "/health",
    }


app.include_router(api_router)

init_db()


@app.on_event("startup")
def on_startup() -> None:
    t_start = time.monotonic()
    logger.info("=" * 60)
    logger.info("=== Démarrage backend SoilAI ===")
    logger.info(f"Project     : {settings.project_name}")
    logger.info(f"API Version : {settings.api_version}")
    logger.info(f"Root dir    : {settings.root_dir}")
    logger.info(f"Models dir  : {settings.models_dir}")
    logger.info(f"Active family: {settings.active_model_family}")
    logger.info(f"Active model dir: {settings.active_model_dir}")
    logger.info(f"Active model dir exists: {settings.active_model_dir.exists()}")
    logger.info(f"Database path : {settings.database_path}")
    logger.info(f"Database exists: {settings.database_path.exists()}")

    # ── Step 1 – Clear any stale cache, then warm it once ───────────────────
    reset_global_models()
    logger.info("[Startup] reset_global_models done  %.3fs", time.monotonic() - t_start)

    preload_models = os.environ.get("PRELOAD_MODELS_ON_STARTUP", "0").lower() in {
        "1", "true", "yes", "on"
    }
    if preload_models:
        try:
            t_load = time.monotonic()
            models = get_global_models(settings)
            model_summary = {k: len(v) for k, v in models.items() if k != "_elapsed_s"}
            model_total  = sum(len(v) for k, v in models.items() if k != "_elapsed_s")
            logger.info(
                "[Startup] Modèles préchargés (%d modèles)  labels=%s  elapsed=%.3fs",
                model_total, model_summary, time.monotonic() - t_load,
            )
        except Exception as exc:
            logger.warning(
                "[Startup] Échec préchargement modèles (prévisible si aucun entraîné) : %s",
                exc,
            )
    else:
        logger.info(
            "[Startup] Preload modèles désactivé (PRELOAD_MODELS_ON_STARTUP=0) ; "
            "chargement à la demande."
        )

    init_db()
    logger.info("[Startup] Ready  total_elapsed=%.3fs", time.monotonic() - t_start)
    logger.info("=== Backend prêt ===")


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("=== Arrêt backend SoilAI ===")