from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.db.init_db import init_db


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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Backend Webbeck API is running",
        "docs": "/docs",
        "health": "/health",
    }
app.include_router(api_router)

init_db()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
