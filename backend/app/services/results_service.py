from __future__ import annotations

from pathlib import Path

from app.core.config import Settings
from app.schemas.results import ModelSummary, ResultsSummaryResponse
from app.services.artifact_service import ArtifactService


class ResultsService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.artifacts = ArtifactService(settings)

    def _summary_from_family(self, family: str, directory: Path) -> ModelSummary:
        bundle = self.artifacts.load_bundle(family, directory)
        return ModelSummary(
            model_name=f"SoilAI {family.replace('_', ' ').title()}",
            family=family,
            hamming_accuracy=bundle.valid_results.get("hamming_accuracy")
            or bundle.test_results.get("hamming_accuracy"),
            macro_f1_global=bundle.valid_results.get("macro_f1_global")
            or bundle.test_results.get("macro_f1_global"),
            per_label_accuracy=bundle.valid_results.get("per_label_accuracy")
            or bundle.test_results.get("per_label_accuracy", {}),
            thresholds=bundle.valid_results.get("thresholds")
            or bundle.test_results.get("thresholds")
            or bundle.thresholds,
            sources={
                "results_valid": str(directory / "results_valid.json"),
                "results_test": str(directory / "results_test.json"),
            },
        )

    def get_summary(self) -> ResultsSummaryResponse:
        candidates = [
            ("efficientnetv2l", self.settings.active_model_dir),
            ("densenet201", self.settings.densenet201_dir),
            ("mobilenetv2", self.settings.mobilenetv2_dir),
        ]

        summaries = [self._summary_from_family(family, directory) for family, directory in candidates if directory.exists()]
        if not summaries:
            empty = ModelSummary(model_name="Unavailable", family="unknown")
            return ResultsSummaryResponse(
                best_model=empty,
                models=[],
                baseline_notes=["No usable result artifact was found."],
            )

        best_model = max(
            summaries,
            key=lambda item: float(item.hamming_accuracy or item.macro_f1_global or 0.0),
        )

        notes = [
            "The best model is selected using hamming accuracy whenever it is available.",
            "All displayed metrics come directly from the project's training artifacts.",
            "EfficientNetV2L is the recommended product showcase model, while DenseNet201 is the strongest scientific comparison baseline.",
        ]

        return ResultsSummaryResponse(best_model=best_model, models=summaries, baseline_notes=notes)
