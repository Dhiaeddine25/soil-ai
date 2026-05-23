from __future__ import annotations

import json
import logging
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Callable
from uuid import uuid4

import numpy as np
from PIL import Image, ImageOps

# Must run before importing TensorFlow so runtime options are respected.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

# ── TensorFlow/Keras primed once at module import time ───────────────────────
# A full TF import + backend initialization takes ~1–3 s on first use.
# Importing here shifts that cost to process start-up (FastAPI / uvicorn)
# instead of hiding it inside request latency.
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model as _tf_load_model
    from tensorflow.keras.applications import (
        densenet as _densenet_mod,
        efficientnet_v2 as _effnet_mod,
        mobilenet_v2 as _mobnet_mod,
    )
    tf.get_logger().setLevel("ERROR")
    try:
        from absl import logging as _absl_logging

        _absl_logging.set_verbosity(_absl_logging.ERROR)
        _absl_logging.set_stderrthreshold("error")
    except Exception:
        pass
    _TF_AVAILABLE = True
except Exception:  # pragma: no cover – TF not installed in test env
    _TF_AVAILABLE = False
    _tf_load_model = None  # type: ignore[assignment]

from app.core.config import Settings
from app.schemas.agronomic_advice import AgronomicAdvice
from app.schemas.prediction import ImageQualityMetadata, NutrientPrediction
from app.schemas.prediction_quality import ConfidenceDetails, QualityCheck
from app.services.agronomic_advice_service import AgronomicAdviceService
from app.services.image_quality_service import ImageQualityService, PreparedImage
from app.services.prediction_decision_service import PredictionDecisionService
from app.services.probability_calibration import CalibrationResult, ProbabilityCalibrationService

logger = logging.getLogger(__name__)

# ── Labels ─────────────────────────────────────────────────────────────────────

LABELS = ["K0", "K1", "K2", "N0", "N1", "N2", "P0", "P1"]
NUTRIENTS: dict[str, list[str]] = {
    "K": ["K0", "K1", "K2"],
    "N": ["N0", "N1", "N2"],
    "P": ["P0", "P1"],
}
ENSEMBLE_FAMILIES = {"efficientnetv2l", "mobilenetv2", "densenet201"}

# ── TF preprocessing callables resolved once at import ────────────────────────

if _TF_AVAILABLE:
    _TF_LOAD_FN: dict[str, Callable] = {}  # filled below
else:
    _TF_LOAD_FN = {}


def _tf_load(artifact: Path) -> object | None:
    """Thin wrapper around ``tf.keras.models.load_model`` that matches the
    single-argument ``(artifact_path) → model`` signature used everywhere
    in ``_load_models_from_disk``."""
    return _tf_load_model(str(artifact), compile=False)  # type: ignore[return-value]


for _fam in ("densenet", "densenet201", "densenet_opti",
             "efficientnetv2l", "mobilenetv2", "vscode"):
    _TF_LOAD_FN[_fam] = _tf_load  # all families share the same loader


def _identity_preprocess(img: np.ndarray) -> np.ndarray:
    return img


def _extract_probability(raw_output: np.ndarray) -> float:
    flat = np.asarray(raw_output, dtype=np.float32).ravel()
    if flat.size == 0:
        return 0.0
    if flat.size == 1:
        return float(flat[0])
    if flat.size == 2:
        return float(flat[1])
    return float(np.max(flat))


# ── Global model cache: loaded once at startup, shared across all requests ────
# Pattern: readers call get_global_models(); the Fn returns the cached dict
# immediately (no disk I/O after the first warm call).
# reset_global_models() puts _GLOBAL_MODELS back to None so a fresh call
# re-scans disk (handy in dev when retraining a model).

_GLOBAL_MODELS: dict[str, list] | None = None
_GLOBAL_MODELS_LOCK = threading.RLock()
_GLOBAL_CALIBRATION_PROFILE: dict[str, float] | None = None
_GLOBAL_CALIBRATION_LOCK = threading.RLock()


def get_global_models(settings: Settings) -> dict[str, list]:
    """Return models from cache; load-and-cache on first call after reset."""
    global _GLOBAL_MODELS
    if _GLOBAL_MODELS is not None:
        logger.debug("[ML] get_global_models → cache hit (%d families)", len(_GLOBAL_MODELS))
        return _GLOBAL_MODELS
    with _GLOBAL_MODELS_LOCK:
        if _GLOBAL_MODELS is not None:
            logger.debug("[ML] get_global_models → cache hit after lock (%d families)", len(_GLOBAL_MODELS))
            return _GLOBAL_MODELS
        logger.info("[ML] get_global_models -> first call; loading from disk...")
        t0 = time.monotonic()
        _GLOBAL_MODELS = _load_models_from_disk(settings)
        logger.info("[ML] get_global_models → disk load done in %.3fs", time.monotonic() - t0)
    return _GLOBAL_MODELS


def reset_global_models() -> None:
    """Invalidate the cache so the next call re-loads from disk."""
    global _GLOBAL_MODELS
    logger.info("[ML] reset_global_models: cache cleared")
    _GLOBAL_MODELS = None


# ── Disk helpers ───────────────────────────────────────────────────────────────

def _load_models_from_disk(settings: Settings) -> dict[str, list]:
    """Discover and load every model artifact found under the project root."""
    from app.services.ml_prediction_service import LoadedModel  # local import, safe

    loaded: dict[str, list] = {label: [] for label in LABELS}
    root = settings.root_dir
    families: list[tuple[str, Path]] = [
        (d.name.replace("npk_models_", ""), d)
        for d in sorted(root.glob("npk_models_*"))
        if d.is_dir()
    ]

    families = [item for item in families if item[0] in ENSEMBLE_FAMILIES]
    logger.info("[ML] Ensemble families enabled: %s", sorted(ENSEMBLE_FAMILIES))

    if not families:
        logger.warning(
            "[ML] No model families found under %s", root
        )
        return loaded

    t_family = time.monotonic()
    for family_name, family_dir in families:
        t0 = time.monotonic()
        backend, loader, preprocess_fn = _backend_spec(family_name)
        if loader is None:
            logger.warning("[ML] No loader for family '%s' – skipped", family_name)
            continue

        weight = _family_weight(family_dir)
        for label in LABELS:
            artifact = _artifact_path(family_dir, label)
            if artifact is None:
                continue
            try:
                model = loader(artifact)
                logger.info("[ML] Loaded model family=%s label=%s backend=%s path=%s", family_name, label, backend, artifact)
                loaded[label].append(
                    LoadedModel(
                        family=family_name,
                        label=label,
                        path=artifact,
                        threshold=_threshold(family_dir, label),
                        weight=weight,
                        backend=backend,
                        model=model,
                        preprocess=preprocess_fn,
                    )
                )
            except Exception:
                logger.exception("[ML] Failed to load %s/%s", family_name, label)

        logger.info(
            "[ML] Family '%s' loaded in %.2fs (%d labels found)",
            family_name, time.monotonic() - t0,
            sum(1 for v in loaded.values() if v),
        )

    summary = {k: len(v) for k, v in loaded.items()}
    total   = sum(summary.values())
    _set_global_calibration_profile(
        ProbabilityCalibrationService.build_entropy_profile(
            [family_dir for _, family_dir in families],
            settings.calibration_entropy_fallback,
        )
    )
    _warmup_models(loaded)
    logger.info(
        "[ML] All models loaded in %.2fs – per-label count: %s  [TOTAL=%d models]",
        time.monotonic() - t_family, summary, total,
    )
    return loaded


def _set_global_calibration_profile(profile: dict[str, float]) -> None:
    global _GLOBAL_CALIBRATION_PROFILE
    with _GLOBAL_CALIBRATION_LOCK:
        _GLOBAL_CALIBRATION_PROFILE = profile


def _get_global_calibration_profile(settings: Settings) -> dict[str, float]:
    global _GLOBAL_CALIBRATION_PROFILE
    if _GLOBAL_CALIBRATION_PROFILE is not None:
        return _GLOBAL_CALIBRATION_PROFILE
    with _GLOBAL_CALIBRATION_LOCK:
        if _GLOBAL_CALIBRATION_PROFILE is not None:
            return _GLOBAL_CALIBRATION_PROFILE
        family_dirs = [
            d for d in sorted(settings.root_dir.glob("npk_models_*"))
            if d.is_dir() and d.name.replace("npk_models_", "") in ENSEMBLE_FAMILIES
        ]
        _GLOBAL_CALIBRATION_PROFILE = ProbabilityCalibrationService.build_entropy_profile(
            family_dirs,
            settings.calibration_entropy_fallback,
        )
        return _GLOBAL_CALIBRATION_PROFILE


def _warmup_models(models: dict[str, list]) -> None:
    """Run one dry prediction per loaded model to prebuild TF graphs.

    This shifts one-time graph tracing overhead from first user request to startup.
    """
    dummy = np.zeros((224, 224, 3), dtype=np.float32)
    warmed = 0
    t0 = time.monotonic()
    for label_models in models.values():
        for loaded in label_models:
            try:
                processed = loaded.preprocess(dummy)
                batch = np.expand_dims(processed, axis=0)
                if loaded.backend == "tensorflow":
                    loaded.model.predict(batch, verbose=0)  # type: ignore[union-attr]
                else:
                    import torch

                    tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).float()
                    with torch.no_grad():
                        loaded.model(tensor)
                warmed += 1
            except Exception:
                logger.exception("[ML] Warmup failed for family=%s label=%s", loaded.family, loaded.label)
    logger.info("[ML] Warmup complete in %.2fs (%d models)", time.monotonic() - t0, warmed)


@dataclass(frozen=True)
class LoadedModel:
    family:  str
    label:   str
    path:    Path
    threshold: float
    weight:  float
    backend: str
    model:   object
    preprocess: Callable[[np.ndarray], np.ndarray]


def _backend_spec(family_name: str) -> tuple[str, Callable | None, Callable]:
    """Return (backend, loader_fn, preprocess_fn) for the given family.

    TF functions are already registered at module level (primed at import),
    so this is now a pure O(1) dict lookup with zero import overhead.
    """
    if family_name not in _TF_LOAD_FN:
        return "unknown", None, _identity_preprocess
    return "tensorflow", _tf_load, _identity_preprocess


def _artifact_path(family_dir: Path, label: str) -> Path | None:
    """Return the first matching model artifact for *label* inside *family_dir*."""
    label_dir = family_dir / label
    for candidate in (label_dir / "model.keras", label_dir / "model.h5"):
        if candidate.exists():
            logger.info("[ML] Artifact found family_dir=%s label=%s path=%s", family_dir, label, candidate)
            return candidate
        logger.warning("[ML] Artifact missing family_dir=%s label=%s path=%s", family_dir, label, candidate)
    # PyTorch fallback
    pth = list(label_dir.glob("*.pth"))
    if pth and __import__("importlib").util.find_spec("torch") is not None:
        logger.info("[ML] PyTorch artifact found family_dir=%s label=%s path=%s", family_dir, label, pth[0])
        return pth[0]
    return None


def _threshold(family_dir: Path, label: str) -> float:
    """Read decision threshold from JSON; fall back to 0.5."""
    for candidate in (family_dir / f"seuil_{label}.json", family_dir / "seuils.json"):
        if not candidate.exists():
            continue
        try:
            with candidate.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            if isinstance(payload, dict) and "seuil" in payload:
                return float(payload["seuil"])
        except Exception:
            continue
    return 0.5


def _family_weight(family_dir: Path) -> float:
    """Derive family weight from validation/test Hamming accuracy."""
    for candidate in (family_dir / "results_valid.json", family_dir / "results_test.json"):
        if not candidate.exists():
            continue
        try:
            with candidate.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            hamming = float(payload.get("hamming_accuracy", 0.0))
            if hamming > 0:
                return max(0.1, hamming)
        except Exception:
            continue
    return 1.0


def _model_name_from_cache(models: dict) -> str:
    """Return a human-readable ensemble name from the cached model dict."""
    families = {
        e.family
        for v in models.values()
        for e in v
        if hasattr(e, "family")
    }
    if not families:
        return "SoilAI ML Ensemble"
    return "SoilAI " + " + ".join(f.capitalize() for f in sorted(families))


# ════════════════════════════════════════════════════════════════════════════════
# Main prediction service
# ═══════════════════════════════════════════════════════════════════════════════

class MLPredictionService:
    """Synchronous prediction service—run via ``run_in_threadpool``."""

    def __init__(self, settings: Settings) -> None:
        self.settings      = settings
        self.image_quality = ImageQualityService(settings)
        self.decision      = PredictionDecisionService(settings)
        self.advice        = AgronomicAdviceService()
        self.calibration   = ProbabilityCalibrationService(settings, _get_global_calibration_profile(settings))

    def load_models(self) -> dict[str, list]:
        """Backward-compatible alias – delegates to the module-level cache."""
        return get_global_models(self.settings)

    # ─── Public entry point ───────────────────────────────────────────────────

    def predict_npk(
        self,
        image_bytes: bytes,
        image_name:   str | None = None,
        parcel_id:    str | None = None,
        user_id:      str | None = None,
    ) -> dict:
        """Synchronous endpoint.  Must be called from a thread-pool."""
        t_total     = time.monotonic()
        analysis_id = str(uuid4())
        logger.info(
            "[ML] predict_npk start analysis_id=%s image=%s user=%s parcel=%s bytes=%d",
            analysis_id, image_name, user_id, parcel_id, len(image_bytes),
        )

        # ── 1. Save image to disk ─────────────────────────────────────────────
        t0 = time.monotonic()
        logger.info("[ML] PREPROCESS START image=%s", image_name)
        try:
            image_path = self._save_image(image_bytes, analysis_id, image_name)
            logger.info("[ML] PREPROCESS END %.3fs image_saved=%s", time.monotonic() - t0, image_path)
        except Exception:
            logger.exception("[ML] save_image FAILED")
            raise

        # ── 2. Quality check + image preparation ────────────────────────────
        t0 = time.monotonic()
        try:
            prepared: PreparedImage = self.image_quality.prepare_for_prediction(image_bytes)
            quality_check = prepared.quality_check
            image_quality_score = prepared.image_quality_score
            image_quality_warning = prepared.image_quality_warning
            image_quality_recommendations = prepared.image_quality_recommendations
            logger.info("[ML] QUALITY CHECK OK valid=%s width=%d height=%d brightness=%.2f contrast=%.2f sharpness=%.2f issues=%s %.3fs",
                        quality_check.valid, quality_check.width, quality_check.height,
                        quality_check.brightness, quality_check.contrast, quality_check.sharpness,
                        quality_check.issues, time.monotonic() - t0)
        except Exception:
            logger.exception("[ML] quality_check FAILED")
            raise

        # ── 3. First-pass refusal ─────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            refusal = self._refusal_first_pass(quality_check)
            if refusal["refused"]:
                logger.warning(
                    "[ML] quality gate flagged image (pass 1) but inference will continue: %s",
                    refusal["reason"],
                )
            logger.debug("[ML] refusal pass-1 %.3fs", time.monotonic() - t0)
        except Exception:
            logger.exception("[ML] refusal pass-1 FAILED")
            # continue permissive on refusal errors

        # ── 4. Load models from global cache ─────────────────────────────────
        t0 = time.monotonic()
        models: dict[str, list] = {}
        logger.info("[ML] MODEL LOAD START from global cache")
        try:
            models = get_global_models(self.settings)
            model_info = {k: len(v) for k, v in models.items() if k != "_elapsed_s"}
            logger.info("[ML] MODEL LOAD END labels=%s %.3fs", model_info, time.monotonic() - t0)
            if not any(models.values()):
                return self._build_refusal_payload(
                    analysis_id=analysis_id,
                    image_name=image_name,
                    image_path=image_path,
                    user_id=user_id,
                    parcel_id=parcel_id,
                    quality_check=quality_check,
                    reason="aucun_modele_disponible",
                )
        except Exception:
            logger.exception("[ML] get_global_models FAILED")
            raise

        # ── 5. Predict probabilities (uses cached pixels from refusal pass 1) ─
        t0 = time.monotonic()
        print("PIPELINE STEP: MODEL")
        logger.info("[ML] PREDICTION START models=%d", sum(len(v) for v in models.values() if v))
        try:
            if prepared.image_224 is None:
                raise RuntimeError("image_224 missing after successful quality preparation")
            logger.info(
                "[ML] PREPARED INPUT stats shape=%s dtype=%s min=%.6f max=%.6f mean=%.6f std=%.6f",
                prepared.image_224.shape,
                prepared.image_224.dtype,
                float(np.min(prepared.image_224)),
                float(np.max(prepared.image_224)),
                float(np.mean(prepared.image_224)),
                float(np.std(prepared.image_224)),
            )
            probabilities, debug_payload, calibration_results = self._predict_probabilities(models, prepared.image_224)
            logger.info("[ML] PREDICTION END %.3fs probs=%s", time.monotonic() - t0, probabilities)
        except Exception:
            logger.exception("[ML] probabilities FAILED")
            raise

        # ── 6. Select prediction ──────────────────────────────────────────────
        try:
            prediction, selected_scores = self._select_prediction(models, probabilities)
            logger.info("[ML] SELECTED SCORES %s", selected_scores)
            if any(score < 0 for score in selected_scores.values()):
                logger.warning("[ML] prediction below learned thresholds; keeping real model outputs: %s", selected_scores)
        except Exception:
            logger.exception("[ML] _select_prediction FAILED")
            raise

        # ── 8. Confidence details ─────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            confidence_details = self.decision.build_confidence_details(probabilities)
            logger.debug("[ML] confidence_details  %.3fs  max_prob=%.3f margin=%.3f", time.monotonic() - t0, confidence_details.max_prob, confidence_details.margin)
        except Exception:
            logger.exception("[ML] confidence_details FAILED")
            raise

        # ── 8. Second-pass refusal (uses cached pixels, no re-read) ──────────
        try:
            refusal2 = self._refusal_second_pass(quality_check, confidence_details)
            if refusal2["refused"]:
                logger.warning(
                    "[ML] quality gate flagged image (pass 2) but inference will continue: %s max_prob=%.3f margin=%.3f %.3fs",
                    refusal2["reason"], confidence_details.max_prob, confidence_details.margin, time.monotonic() - t_total,
                )
        except Exception:
            logger.exception("[ML] refusal pass-2 FAILED")

        # ── 9. Confidence score ───────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            confidence = self.calculate_confidence(probabilities, prediction)
            logger.debug("[ML] confidence  %.3fs  %s", time.monotonic() - t0, confidence)
        except Exception:
            logger.exception("[ML] calculate_confidence FAILED")
            raise

        # ── 10. Soil score ───────────────────────────────────────────────────
        try:
            soil_health_score, uncertainty_metrics, score_breakdown = self.calculate_soil_health_score(probabilities, calibration_results)
            score = int(round(soil_health_score))
        except Exception:
            logger.exception("[ML] calculate_soil_score FAILED")
            raise

        # ── 11. Agronomic advice ──────────────────────────────────────────────
        try:
            agronomic_advice = self.advice.build(NutrientPrediction(**prediction))
        except Exception:
            logger.exception("[ML] agronomic advice FAILED")
            raise

        # ── 12. Field advice ─────────────────────────────────────────────────
        try:
            field_advice, field_disclaimer = self.generate_field_advice(
                prediction, probabilities, score, confidence,
            )
        except Exception:
            logger.exception("[ML] field advice FAILED")
            raise

        # ── 13. Status ───────────────────────────────────────────────────────
        try:
            status = self.decision.determine_status(quality_check, confidence, confidence_details)
        except Exception:
            logger.exception("[ML] determine_status FAILED")
            raise

        # ── 14. Messages ─────────────────────────────────────────────────────
        try:
            recommendation_message = self.decision.recommendation_message(status)
            warning_message        = self.decision.warning_message(status, quality_check)
        except Exception:
            logger.exception("[ML] messages FAILED")
            recommendation_message = "Voir les résultats"
            warning_message        = ""

        quality_warning = image_quality_warning or None
        if quality_warning == 'low_image_quality':
            warning_message = (
                "Qualité d'image faible: " + ", ".join(quality_check.issues or ["metriques visuelles faibles"])
            )
        elif quality_warning is None and not warning_message:
            warning_message = ""

        elapsed_total = time.monotonic() - t_total
        print("PIPELINE STEP: RESPONSE")
        logger.info(
            "[ML] predict_npk done  elapsed=%.3fs  status=%s  score=%s  confidence=%.4f",
            elapsed_total, status, score, confidence,
        )

        return {
            "analysis_id":          analysis_id,
            "model_name":           _model_name_from_cache(models),
            "npk_prediction":       NutrientPrediction(**prediction),
            "prediction":           prediction,
            "nitrogen":             self._nutrient_detail("N", prediction["N_level"], probabilities, calibration_results.get("N")),
            "phosphorus":           self._nutrient_detail("P", prediction["P_level"], probabilities, calibration_results.get("P")),
            "potassium":            self._nutrient_detail("K", prediction["K_level"], probabilities, calibration_results.get("K")),
            "confidence":           confidence,
            "status":               status,
            "can_trust_result":     self.decision.can_trust(status),
            "quality_check":        quality_check,
            "confidence_details":   confidence_details,
            "interpretation":       self._interpretation(prediction, confidence, status),
            "recommendation":       recommendation_message,
            "agronomic_advice":     agronomic_advice,
            "field_advice":         field_advice,
            "field_disclaimer":     field_disclaimer,
            "warning_message":      warning_message,
            "recommendation_message": recommendation_message,
            "warning":              quality_warning,
            "recommendations":      image_quality_recommendations,
            "image_quality_score":   image_quality_score,
            "image_quality":        ImageQualityMetadata(
                image_quality_score=image_quality_score,
                warning=quality_warning,
                recommendations=image_quality_recommendations,
            ),
            "is_mock":              False,
            "timestamp":            datetime.now(timezone.utc),
            "source":               f"uploaded_image:{user_id}" if user_id else "uploaded_image",
            "model_status":         "ready",
            "probabilities":        probabilities,
            "soil_health_score":    soil_health_score,
            "uncertainty_metrics":  uncertainty_metrics,
            "debug":                debug_payload if self.settings.debug_predictions else None,
            "score_breakdown":      score_breakdown if self.settings.debug_predictions else None,
            "score":                score,
            "refused":              False,
            "refusal_reason":       None,
            "image_name":           image_name,
            "image_url":            f"/history/images/{analysis_id}",
            "image_path":           str(image_path),
            "parcel_id":            parcel_id,
        }

    # ─── Pixel preload / 224×224 build (called once per prediction) ──────────

    # ─── Refusal detection ───────────────────────────────────────────────────

    def _refusal_first_pass(
        self, quality_check: QualityCheck,
    ) -> dict[str, object]:
        """Compatibility helper that now only reports quality advisories."""
        if not quality_check.valid:
            logger.info("[Refusal] First pass: quality invalid, issues=%s", quality_check.issues)
            return {"refused": False, "reason": "image_non_exploitable"}

        logger.info("[Refusal] First pass: quality valid, accepting")
        return {"refused": False, "reason": None}

    def _refusal_second_pass(
        self,
        quality_check:     QualityCheck,
        confidence_details: ConfidenceDetails | None = None,
    ) -> dict[str, object]:
        """Compatibility helper that now only reports confidence advisories."""
        if confidence_details is None:
            return {"refused": False, "reason": None}
        logger.info("[Refusal] Second pass: confidence advisories only (max_prob=%.3f, margin=%.3f)",
                   confidence_details.max_prob, confidence_details.margin)
        return {"refused": False, "reason": None}

    # Keep original signature for any external callers ─────────────────────────
    def refusal_detection(
        self,
        image_bytes:       bytes,
        quality_check:     QualityCheck,
        confidence_details: ConfidenceDetails | None = None,
    ) -> dict[str, object]:
        """Backward-compatible single-call refusal detector kept for callers.

        It now reports advisories only and never blocks inference for valid images.
        """
        # Quality check
        if not quality_check.valid:
            logger.info("[Refusal] Image invalid: %s", quality_check.issues)
            return {"refused": False, "reason": "image_non_exploitable"}
        
        if confidence_details:
            logger.info("[Refusal] Confidence advisories only: max_prob=%.3f margin=%.3f",
                       confidence_details.max_prob, confidence_details.margin)

        logger.info("[Refusal] No refusal reasons, accepting image")
        return {"refused": False, "reason": None}

    # ─── Prediction ───────────────────────────────────────────────────────────

    def _predict_probabilities(
        self, models: dict[str, list], img_224: np.ndarray,
    ) -> tuple[dict[str, float], dict[str, object] | None, dict[str, CalibrationResult]]:
        """Run every loaded model on the same 224×224 pre-built array."""

        logger.info(
            "[ML] INPUT TENSOR stats shape=%s dtype=%s min=%.3f max=%.3f mean=%.3f",
            img_224.shape,
            img_224.dtype,
            float(np.min(img_224)),
            float(np.max(img_224)),
            float(np.mean(img_224)),
        )

        total_model_count = sum(len(models.get(label, [])) for label in LABELS)
        if total_model_count <= 0:
            return {label: 0.0 for label in LABELS}, None, {}

        predictions_by_label: dict[str, list[tuple[float, float, list[float], tuple[int, ...] | None]]] = {
            label: [] for label in LABELS
        }
        debug_models: list[dict[str, object]] = []

        # Run per-model inference concurrently to reduce end-to-end latency.
        max_workers = min(8, total_model_count)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for label in LABELS:
                for loaded in models.get(label, []):
                    future = executor.submit(self._predict_with_model, loaded, img_224)
                    futures[future] = (label, loaded.weight)

            for future in as_completed(futures):
                label, weight = futures[future]
                try:
                    prob, raw_output, output_shape = future.result()
                except Exception:
                    logger.exception("[ML] concurrent predict failed for label=%s", label)
                    prob = 0.0
                    raw_output = []
                    output_shape = None
                predictions_by_label[label].append((float(prob), weight, list(raw_output), output_shape))
                if self.settings.debug_predictions:
                    debug_models.append(
                        {
                            "label": label,
                            "weight": weight,
                            "probability": float(prob),
                            "raw_output": list(raw_output),
                            "output_shape": list(output_shape) if output_shape is not None else None,
                        }
                    )

        raw_probabilities: dict[str, float] = {label: 0.0 for label in LABELS}
        for label in LABELS:
            values_and_weights = predictions_by_label.get(label, [])
            if not values_and_weights:
                continue

            values = [item[0] for item in values_and_weights]
            weights = [item[1] for item in values_and_weights]

            w_arr = np.asarray(weights, dtype=np.float32)
            if w_arr.sum() <= 0:
                w_arr = np.ones_like(w_arr)
            raw_probabilities[label] = float(
                np.average(np.asarray(values, dtype=np.float32), weights=w_arr)
            )
            logger.debug("[ML]  label=%s  n_models=%d  prob=%.6f", label, len(values), raw_probabilities[label])

        logger.info(
            "[ML] RAW PROBABILITIES K=%s N=%s P=%s",
            {label: raw_probabilities[label] for label in NUTRIENTS["K"]},
            {label: raw_probabilities[label] for label in NUTRIENTS["N"]},
            {label: raw_probabilities[label] for label in NUTRIENTS["P"]},
        )
        probabilities, calibration_results = self.calibration.calibrate_probabilities(raw_probabilities)
        logger.info(
            "[ML] CALIBRATED PROBABILITIES K=%s N=%s P=%s",
            {label: probabilities[label] for label in NUTRIENTS["K"]},
            {label: probabilities[label] for label in NUTRIENTS["N"]},
            {label: probabilities[label] for label in NUTRIENTS["P"]},
        )
        debug_payload: dict[str, object] | None = None
        if self.settings.debug_predictions:
            debug_payload = {
                "calibration_mode": "gamma",
                "calibration_factor": self.calibration._gamma(),
                "temperature_proxy": float(self.settings.calibration_temperature),
                "entropy_baseline": {nutrient: result.entropy_baseline for nutrient, result in calibration_results.items()},
                "raw_probabilities": raw_probabilities,
                "calibrated_probabilities": probabilities,
                "entropy_before": {nutrient: result.raw_entropy for nutrient, result in calibration_results.items()},
                "entropy_after": {nutrient: result.calibrated_entropy for nutrient, result in calibration_results.items()},
                "uncertainty_adjustment": {nutrient: result.uncertainty_adjustment for nutrient, result in calibration_results.items()},
                "models": debug_models,
            }
        return probabilities, debug_payload, calibration_results

    def _predict_with_model(self, loaded: LoadedModel, img_224: np.ndarray) -> tuple[float, list[float], tuple[int, ...] | None]:
        """Run a single model inference on a pre-built 224×224 float32 array."""
        import time as _time
        t_infer = _time.monotonic()
        logger.info("[ML] MODEL PREDICT START label=%s family=%s path=%s shape=%s threshold=%.4f", loaded.label, loaded.family, loaded.path, img_224.shape, loaded.threshold)
        try:
            img_array = img_224.astype(np.float32, copy=False)
            logger.info(
                "[ML] MODEL INPUT stats label=%s family=%s min=%.6f max=%.6f mean=%.6f std=%.6f",
                loaded.label,
                loaded.family,
                float(np.min(img_array)),
                float(np.max(img_array)),
                float(np.mean(img_array)),
                float(np.std(img_array)),
            )
            logger.info("[ML] SHAPE BEFORE EXPAND: %s", img_array.shape)
            batch = np.expand_dims(img_array, axis=0)
            logger.info("[ML] FINAL SHAPE: %s", batch.shape)

            if loaded.backend == "tensorflow":
                logger.info("[ML] CALLING TENSORFLOW PREDICT")
                result = loaded.model(batch, training=False)  # type: ignore[operator]
                flat = np.asarray(result).ravel()
                logger.info(
                    "[ML] MODEL RAW OUTPUT label=%s family=%s path=%s output_shape=%s values=%s",
                    loaded.label,
                    loaded.family,
                    loaded.path,
                    getattr(result, "shape", None),
                    np.array2string(flat, precision=6, separator=", "),
                )
                prob = _extract_probability(flat)
                output_shape = tuple(result.shape) if hasattr(result, "shape") else None
            else:
                import torch  # lazy – torch is an optional dependency
                tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).float()
                with torch.no_grad():
                    out = loaded.model(tensor)
                flat = out.detach().cpu().numpy().ravel()
                logger.info(
                    "[ML] MODEL RAW OUTPUT label=%s family=%s path=%s output_shape=%s values=%s",
                    loaded.label,
                    loaded.family,
                    loaded.path,
                    tuple(out.shape),
                    np.array2string(flat, precision=6, separator=", "),
                )
                prob = _extract_probability(flat)
                output_shape = tuple(out.shape)
            logger.info(
                "[ML] MODEL PREDICT END label=%s family=%s path=%s elapsed=%.3fs prob=%.6f",
                loaded.label,
                loaded.family,
                loaded.path,
                _time.monotonic() - t_infer,
                prob,
            )
            return prob, flat.tolist(), output_shape
        except Exception as e:
            logger.exception("[ML] MODEL PREDICT FAILED label=%s error=%s", loaded.label, e)
            return 0.0, [], None

    def _select_prediction(self, models: dict[str, list], probabilities: dict[str, float]) -> tuple[dict[str, str], dict[str, float]]:
        """Choose the strongest label per nutrient, but require a threshold margin."""
        prediction: dict[str, str] = {}
        selected_scores: dict[str, float] = {}

        for nutrient, labels in NUTRIENTS.items():
            best_label = None
            best_score = float("-inf")
            for label in labels:
                label_probability = float(probabilities.get(label, 0.0))
                label_models = models.get(label, [])
                if label_models:
                    threshold = float(np.mean([loaded.threshold for loaded in label_models]))
                else:
                    threshold = 0.5
                score = label_probability - threshold
                if score > best_score:
                    best_score = score
                    best_label = label

            if best_label is None:
                raise RuntimeError(f"No candidate label found for nutrient {nutrient}")

            prediction[f"{nutrient}_level"] = best_label
            selected_scores[nutrient] = round(best_score, 6)

        return prediction, selected_scores

    # ─── Post-processing helpers ──────────────────────────────────────────────

    def calculate_confidence(
        self, probabilities: dict[str, float], prediction: dict[str, str],
    ) -> float:
        selected = [
            probabilities.get(prediction.get(f"{nutrient}_level", ""), 0.0)
            for nutrient in ("K", "N", "P")
        ]
        avg = float(np.mean(selected)) if selected else 0.0
        details = self.decision.build_confidence_details(probabilities)
        return round(max(0.0, min(1.0, avg * 0.7 + details.margin * 0.3)), 4)

    def calculate_soil_score(self, probabilities: dict[str, float]) -> int:
        score, _, _ = self.calculate_soil_health_score(probabilities)
        return int(round(score))

    def _entropy(self, values: list[float]) -> float:
        array = np.asarray(values, dtype=np.float32)
        if array.size == 0:
            return 0.0
        total = float(array.sum())
        if total <= 0:
            return 0.0
        normalized = array / total
        entropy = -float(np.sum(np.where(normalized > 0, normalized * np.log(normalized), 0.0)))
        if normalized.size <= 1:
            return 0.0
        return float(entropy / np.log(normalized.size))

    def _nutrient_analysis(
        self,
        nutrient: str,
        probabilities: dict[str, float],
        calibration_result: CalibrationResult | None = None,
    ) -> dict[str, float | list[float] | str]:
        labels = NUTRIENTS[nutrient]
        vector = [max(float(probabilities.get(lbl, 0.0)), 0.0) for lbl in labels]
        raw_vector = calibration_result.raw_probabilities if calibration_result else vector
        calibrated_vector = calibration_result.calibrated_probabilities if calibration_result else vector
        indexed = sorted(calibrated_vector, reverse=True)
        max_prob = float(indexed[0]) if indexed else 0.0
        second_max = float(indexed[1]) if len(indexed) > 1 else 0.0
        variance_index = max(max_prob - second_max, 0.0)
        uncertainty_score = (second_max / max_prob) if max_prob > 0 else 1.0
        raw_entropy = self._entropy(raw_vector)
        entropy = self._entropy(calibrated_vector)
        entropy_baseline = float(calibration_result.entropy_baseline) if calibration_result else float(self.settings.calibration_entropy_fallback)
        entropy_ratio = float(calibration_result.entropy_ratio) if calibration_result else (entropy / entropy_baseline if entropy_baseline > 0 else 1.0)
        uncertainty_adjustment = float(calibration_result.uncertainty_adjustment) if calibration_result else 1.0
        uncertainty_score = min(max(uncertainty_score * uncertainty_adjustment, 0.0), 1.0)
        return {
            "class": labels[int(np.argmax(calibrated_vector))] if calibrated_vector else labels[0],
            "confidence": round(max_prob, 4),
            "probabilities": [round(value, 6) for value in calibrated_vector],
            "raw_probabilities": [round(value, 6) for value in raw_vector],
            "calibrated_probabilities": [round(value, 6) for value in calibrated_vector],
            "raw_entropy": round(raw_entropy, 4),
            "entropy": round(entropy, 4),
            "calibrated_entropy": round(entropy, 4),
            "entropy_baseline": round(entropy_baseline, 4),
            "entropy_ratio": round(entropy_ratio, 4),
            "calibration_factor": round(float(calibration_result.calibration_factor), 4) if calibration_result else round(self.calibration._gamma(), 4),
            "variance_index": round(variance_index, 4),
            "uncertainty_score": round(min(max(uncertainty_score, 0.0), 1.0), 4),
            "uncertainty_adjustment": round(uncertainty_adjustment, 4),
            "softened": bool(calibration_result.softened) if calibration_result else False,
        }

    def _interpret_nutrient_context(self, analysis: dict[str, float | list[float] | str]) -> str:
        confidence = float(analysis.get("confidence", 0.0))
        entropy = float(analysis.get("entropy", 0.0))
        uncertainty = float(analysis.get("uncertainty_score", 1.0))
        if confidence > 0.85 and entropy < 0.45 and uncertainty < 0.45:
            return "état stable"
        if confidence >= 0.5 and entropy >= 0.55:
            return "zone incertaine"
        if confidence < 0.5:
            return "risque de déséquilibre"
        return "lecture intermédiaire"

    def calculate_soil_health_score(
        self,
        probabilities: dict[str, float],
        calibration_results: dict[str, CalibrationResult] | None = None,
    ) -> tuple[float, dict[str, dict[str, float | list[float] | str]], dict[str, float]]:
        k = self._nutrient_analysis("K", probabilities, calibration_results.get("K") if calibration_results else None)
        n = self._nutrient_analysis("N", probabilities, calibration_results.get("N") if calibration_results else None)
        p = self._nutrient_analysis("P", probabilities, calibration_results.get("P") if calibration_results else None)

        max_mean = (float(k["confidence"]) + float(n["confidence"]) + float(p["confidence"])) / 3.0
        uncertainty_penalty = ((float(k["uncertainty_score"]) + float(n["uncertainty_score"]) + float(p["uncertainty_score"])) / 3.0)
        score = (max_mean * 100.0) - (uncertainty_penalty * 10.0)
        score = max(0.0, min(100.0, round(score, 2)))

        uncertainty_metrics = {
            "K": {k_: float(v) if isinstance(v, (int, float)) else v for k_, v in k.items() if k_ != "class" and k_ != "probabilities"},
            "N": {k_: float(v) if isinstance(v, (int, float)) else v for k_, v in n.items() if k_ != "class" and k_ != "probabilities"},
            "P": {k_: float(v) if isinstance(v, (int, float)) else v for k_, v in p.items() if k_ != "class" and k_ != "probabilities"},
        }

        score_breakdown = {
            "max_mean": round(max_mean, 4),
            "uncertainty_penalty": round(uncertainty_penalty, 4),
            "formula": "((K_max + N_max + P_max) / 3) * 100 - (uncertainty_penalty * 10)",
        }
        return score, uncertainty_metrics, score_breakdown

    def _nutrient_detail(
        self,
        nutrient: str,
        label: str,
        probabilities: dict[str, float],
        calibration_result: CalibrationResult | None = None,
    ) -> dict[str, object]:
        analysis = self._nutrient_analysis(nutrient, probabilities, calibration_result)
        analysis["class"] = label
        analysis["signal_score"] = round(1.0 - float(analysis.get("uncertainty_score", 1.0)), 4)
        analysis["interpretation"] = self._interpret_nutrient_context(analysis)
        return analysis

    # ─── Advice ───────────────────────────────────────────────────────────────

    def generate_field_advice(
        self,
        prediction:    dict[str, str],
        probabilities: dict[str, float],
        score:         int,
        confidence:    float,
    ) -> tuple[str, str]:
        parts: list[str] = []

        nutrient_names = {"K": "potassium", "N": "azote", "P": "phosphore"}
        for nutrient, level_key in (("P", "P_level"), ("N", "N_level"), ("K", "K_level")):
            analysis = self._nutrient_analysis(nutrient, probabilities)
            predicted = prediction.get(level_key, NUTRIENTS[nutrient][0])
            if self._interpret_nutrient_context(analysis) == "état stable":
                parts.append(f"Le {nutrient_names[nutrient]} paraît stable ({predicted}).")
            elif self._interpret_nutrient_context(analysis) == "zone incertaine":
                parts.append(f"Le {nutrient_names[nutrient]} est dans une zone incertaine ({predicted}).")
            elif self._interpret_nutrient_context(analysis) == "risque de déséquilibre":
                parts.append(f"Le {nutrient_names[nutrient]} montre un risque de déséquilibre ({predicted}).")
            else:
                parts.append(f"Le {nutrient_names[nutrient]} reste intermédiaire ({predicted}).")

        if   score <= 30: parts.append("Le score global est critique : prioriser une confirmation laboratoire avant action.")
        elif score <= 50: parts.append("Le score global reste faible : une surveillance rapprochée est préférable.")
        elif score <= 70: parts.append("Le score global suggère une surveillance normale avec vérification périodique.")
        else:             parts.append("Le score global est bon : le suivi peut rester préventif.")

        if   confidence < 0.55: disclaimer = "Confiance faible : la lecture reste exploratoire."
        elif confidence < 0.75: disclaimer = "Confiance moyenne : décision prudente recommandée."
        else:                    disclaimer = "Confiance bonne pour un pré-diagnostic indicatif."

        return " ".join(parts), disclaimer

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _interpretation(
        self, prediction: dict[str, str], confidence: float, status: str,
    ) -> str:
        base = f"Lecture NPK : {prediction['K_level']} / {prediction['N_level']} / {prediction['P_level']}."
        if status == "image_non_exploitable":
            return base + " Image non exploitable pour une lecture fiable."
        if confidence > 0.85:
            return base + " état stable sur le plan interprétatif."
        if confidence >= 0.5:
            return base + " zone incertaine à confirmer selon le terrain."
        return base + " risque de déséquilibre à confirmer par examen externe."

    def _build_refusal_payload(
        self,
        *,
        analysis_id:    str,
        image_name:     str | None,
        image_path:     Path,
        user_id:        str | None,
        parcel_id:      str | None,
        quality_check:  QualityCheck,
        reason:         str,
    ) -> dict:
        return {
            "analysis_id":           analysis_id,
            "model_name":            "SoilAI ML Ensemble",
            "npk_prediction":        None,
            "prediction":            None,
            "nitrogen":              None,
            "phosphorus":            None,
            "potassium":             None,
            "confidence":            None,
            "status":                "image_non_exploitable",
            "can_trust_result":      False,
            "quality_check":         quality_check,
            "confidence_details":    None,
            "interpretation":        "Impossible de produire une lecture NPK fiable pour cette image.",
            "recommendation":        "Reprendre une photo plus nette, bien éclairée et centrée sur le sol.",
            "agronomic_advice":      None,
            "field_advice":          None,
            "field_disclaimer":      self.advice.field_disclaimer(),
            "soil_health_score":     None,
            "uncertainty_metrics":   {},
            "debug":                 None,
            "score_breakdown":       {},
            "warning_message":       "Cette image ne permet pas une estimation fiable du sol.",
            "recommendation_message":"Reprendre une photo plus nette, bien éclairée et centrée sur le sol.",
            "warning":               "low_image_quality",
            "recommendations":       ["Reprendre une photo plus nette, bien éclairée et centrée sur le sol."],
            "image_quality_score":   0.0,
            "image_quality":         ImageQualityMetadata(
                image_quality_score=0.0,
                warning="low_image_quality",
                recommendations=["Reprendre une photo plus nette, bien éclairée et centrée sur le sol."],
            ),
            "is_mock":               False,
            "timestamp":             datetime.now(timezone.utc),
            "source":                (f"uploaded_image:{user_id}" if user_id else "uploaded_image"),
            "model_status":          "model_ready",
            "probabilities":         {},
            "score":                 None,
            "refused":               True,
            "refusal_reason":        reason,
            "image_name":            image_name,
            "image_url":             f"/history/images/{analysis_id}",
            "image_path":            str(image_path),
            "parcel_id":             parcel_id,
        }

    def _save_image(
        self, image_bytes: bytes, analysis_id: str, image_name: str | None,
    ) -> Path:
        output_dir = self.settings.root_dir / "data" / "analysis_images"
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(image_name or "analysis.jpg").suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".avif", ".bmp"}:
            suffix = ".jpg"
        image_path = output_dir / f"{analysis_id}{suffix}"
        image_path.write_bytes(image_bytes)
        logger.info("[ML] image saved  path=%s  bytes=%d", image_path, len(image_bytes))
        return image_path