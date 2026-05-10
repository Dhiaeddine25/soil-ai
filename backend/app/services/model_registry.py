from __future__ import annotations

from app.core.config import Settings
from app.services.artifact_service import ArtifactService, LABELS


class ModelRegistry:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.artifacts = ArtifactService(settings)

    def get_registry(self) -> dict:
        families = [
            (self.settings.active_model_family, self.settings.active_model_dir, "active"),
            ("densenet201", self.settings.densenet201_dir, "available"),
            ("mobilenetv2", self.settings.mobilenetv2_dir, "available"),
            ("densenet", self.settings.densenet_dir, "available"),
        ]

        available_models = []
        active_model = None

        for family, directory, status in families:
            if not directory.exists():
                continue
            summary = self.artifacts.build_model_summary(family, directory, status)
            available_models.append(summary)
            if status == "active":
                active_model = summary

        if active_model is None:
            active_model = {
                "model_name": "SoilAI EfficientNetV2L",
                "family": self.settings.active_model_family,
                "status": "mock",
                "version": "1.0.0",
                "description": "Configured reference model for mock mode.",
                "image_size": self.settings.image_size,
                "labels": LABELS,
                "performance": {},
                "artifact_paths": {},
            }

        return {
            "active_model": active_model,
            "available_models": available_models,
            "note": "The backend exposes the real training artifacts first, then a swap-ready inference layer.",
        }
