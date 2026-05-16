from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "SoilAI"
    api_version: str = "v1"
    environment: str = "development"
    active_model_family: str = "efficientnetv2l"
    image_size: int = 320
    confidence_floor: float = 0.55
    # Qualité – seuils très permissifs : accepter presque tout sauf flou extrême / trop sombre
    quality_min_width: int = 32
    quality_min_height: int = 32
    quality_brightness_min: float = 5.0
    quality_brightness_max: float = 250.0
    quality_contrast_min: float = 1.0
    quality_sharpness_min: float = 1.5
    # Dominance verte – très haute pour ne refuser que images entièrement vertes
    refusal_green_dominance_threshold: float = 0.40
    # Confiance – très basse pour accepter presque toutes les prédictions
    refusal_min_confidence: float = 0.10
    refusal_min_margin: float = 0.005
    trust_ok_confidence_min: float = 0.78
    trust_confirm_confidence_min: float = 0.65
    trust_ok_margin_min: float = 0.14
    trust_confirm_margin_min: float = 0.08
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    root_dir: Path = Path(__file__).resolve().parents[3]

    @property
    def models_dir(self) -> Path:
        return self.root_dir

    @property
    def active_model_dir(self) -> Path:
        return self.models_dir / f"npk_models_{self.active_model_family}"

    @property
    def densenet201_dir(self) -> Path:
        return self.models_dir / "npk_models_densenet201"

    @property
    def mobilenetv2_dir(self) -> Path:
        return self.models_dir / "npk_models_mobilenetv2"

    @property
    def densenet_dir(self) -> Path:
        return self.models_dir / "npk_models_densenet"

    @property
    def database_path(self) -> Path:
        return self.root_dir / "backend" / "data" / "soilai.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()