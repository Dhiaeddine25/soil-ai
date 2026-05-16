from __future__ import annotations

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Callable
from uuid import uuid4

import numpy as np
from PIL import Image, ImageOps

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
    _TF_AVAILABLE = True
except Exception:  # pragma: no cover – TF not installed in test env
    _TF_AVAILABLE = False
    _tf_load_model = None  # type: ignore[assignment]

from app.core.config import Settings
from app.schemas.agronomic_advice import AgronomicAdvice
from app.schemas.prediction import NutrientPrediction
from app.schemas.prediction_quality import ConfidenceDetails, QualityCheck
from app.services.agronomic_advice_service import AgronomicAdviceService
from app.services.image_quality_service import ImageQualityService
from app.services.prediction_decision_service import PredictionDecisionService

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
    _TF_PREPROCESS_FN: dict[str, Callable[[np.ndarray], np.ndarray]] = {
        "densenet": _densenet_mod.preprocess_input,
        "densenet201": _densenet_mod.preprocess_input,
        "densenet_opti": _densenet_mod.preprocess_input,
        "efficientnetv2l": _effnet_mod.preprocess_input,
        "mobilenetv2": _mobnet_mod.preprocess_input,
        "vscode": _mobnet_mod.preprocess_input,
    }
    _TF_LOAD_FN: dict[str, Callable] = {}  # filled below
else:
    _TF_PREPROCESS_FN = {}
    _TF_LOAD_FN = {}


def _tf_load(artifact: Path) -> object | None:
    """Thin wrapper around ``tf.keras.models.load_model`` that matches the
    single-argument ``(artifact_path) → model`` signature used everywhere
    in ``_load_models_from_disk``."""
    return _tf_load_model(str(artifact), compile=False)  # type: ignore[return-value]


for _fam in ("densenet", "densenet201", "densenet_opti",
             "efficientnetv2l", "mobilenetv2", "vscode"):
    _TF_LOAD_FN[_fam] = _tf_load  # all families share the same loader


# ── Global model cache: loaded once at startup, shared across all requests ────
# Pattern: readers call get_global_models(); the Fn returns the cached dict
# immediately (no disk I/O after the first warm call).
# reset_global_models() puts _GLOBAL_MODELS back to None so a fresh call
# re-scans disk (handy in dev when retraining a model).

_GLOBAL_MODELS: dict[str, list] | None = None


def get_global_models(settings: Settings) -> dict[str, list]:
    """Return models from cache; load-and-cache on first call after reset."""
    global _GLOBAL_MODELS
    if _GLOBAL_MODELS is not None:
        logger.debug("[ML] get_global_models → cache hit (%d families)", len(_GLOBAL_MODELS))
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
    _warmup_models(loaded)
    logger.info(
        "[ML] All models loaded in %.2fs – per-label count: %s  [TOTAL=%d models]",
        time.monotonic() - t_family, summary, total,
    )
    return loaded


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
    if family_name not in _TF_PREPROCESS_FN:
        return "unknown", None, lambda x: x
    return "tensorflow", _tf_load, _TF_PREPROCESS_FN[family_name]


def _artifact_path(family_dir: Path, label: str) -> Path | None:
    """Return the first matching model artifact for *label* inside *family_dir*."""
    label_dir = family_dir / label
    for candidate in (label_dir / "model.keras", label_dir / "model.h5"):
        if candidate.exists():
            return candidate
    # PyTorch fallback
    pth = list(label_dir.glob("*.pth"))
    if pth and __import__("importlib").util.find_spec("torch") is not None:
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

        # ── 2. Quality check ──────────────────────────────────────────────────
        t0 = time.monotonic()
        try:
            quality_check = self.image_quality.analyze(image_bytes)
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
            refusal = self._refusal_first_pass(quality_check, image_bytes)
            if refusal["refused"]:
                logger.warning(
                    "[ML] image refused (pass 1): %s green_dominance=%.3f %.3fs",
                    refusal["reason"], refusal.get("green_dominance", 0.0), time.monotonic() - t_total,
                )
                return self._build_refusal_payload(
                    analysis_id, image_name, image_path,
                    user_id, parcel_id, quality_check, refusal["reason"],
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
                    analysis_id, image_name, image_path,
                    user_id, parcel_id, quality_check,
                    "aucun_modele_disponible",
                )
        except Exception:
            logger.exception("[ML] get_global_models FAILED")
            raise

        # ── 5. Predict probabilities (uses cached pixels from refusal pass 1) ─
        t0 = time.monotonic()
        logger.info("[ML] PREDICTION START models=%d", sum(len(v) for v in models.values() if v))
        try:
            probabilities = self._predict_probabilities(models)
            logger.info("[ML] PREDICTION END %.3fs probs=%s", time.monotonic() - t0, probabilities)
        except Exception:
            logger.exception("[ML] probabilities FAILED")
            raise

        # ── 6. Select prediction ──────────────────────────────────────────────
        try:
            prediction = self._select_prediction(probabilities)
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
                    "[ML] image refused (pass 2): %s max_prob=%.3f margin=%.3f %.3fs",
                    refusal2["reason"], confidence_details.max_prob, confidence_details.margin, time.monotonic() - t_total,
                )
                return self._build_refusal_payload(
                    analysis_id, image_name, image_path,
                    user_id, parcel_id, quality_check, refusal2["reason"],
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
            score = self.calculate_soil_score(probabilities)
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

        elapsed_total = time.monotonic() - t_total
        logger.info(
            "[ML] predict_npk done  elapsed=%.3fs  status=%s  score=%s  confidence=%.4f",
            elapsed_total, status, score, confidence,
        )

        return {
            "analysis_id":          analysis_id,
            "model_name":           _model_name_from_cache(models),
            "prediction":           prediction,
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
            "is_mock":              False,
            "timestamp":            datetime.now(timezone.utc),
            "source":               f"uploaded_image:{user_id}" if user_id else "uploaded_image",
            "model_status":         "ready",
            "probabilities":        probabilities,
            "score":                score,
            "refused":              False,
            "refusal_reason":       None,
            "image_name":           image_name,
            "image_url":            f"/history/images/{analysis_id}",
            "image_path":           str(image_path),
            "parcel_id":            parcel_id,
        }

    # ─── Pixel preload / 224×224 build (called once per prediction) ──────────

    def _preload_pixels(self, image_bytes: bytes) -> np.ndarray:
        """Load image from *image_bytes* once and return float32 RGB array.

        Called by _refusal_first_pass() and cached; _refusal_second_pass(),
        _prebuild_224() and _predict_probabilities() all reuse the result –
        zero additional BytesIO/Image.open calls per request.
        """
        with Image.open(BytesIO(image_bytes)) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            return np.asarray(img, dtype=np.float32) / 255.0  # H×W×3 float32 ∈ [0,1]

    def _prebuild_224(self, image_bytes: bytes) -> np.ndarray:
        """Resize + build the 224×224 float32 H×W×3 array used by every model.

        Called once and stored/returned by lazy _preload_result cache on self.
        """
        # Fast path: already cached
        if hasattr(self, "_preload_result") and self._preload_result is not None:
            return self._preload_result  # type: ignore[return-value]

        with Image.open(BytesIO(image_bytes)) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            img = img.resize((224, 224), Image.LANCZOS)
            arr = np.asarray(img, dtype=np.float32)  # 224×224×3, raw uint8/float

        self._preload_result = arr
        return arr

    def _preload_for_prediction(self, image_bytes: bytes) -> tuple[np.ndarray, np.ndarray]:
        """One-stop pre-load: returns (pixels_f01, img_224_raw_f32).

        *pixels_f01*  – H×W×3 float32 ∈ [0,1]; used for refusal RGB analysis.
        *img_224_raw_f32* – 224×224×3 float32 raw pixel values; passed to
        each model's preprocess() which converts to the backend's expected range
        (e.g. TF's [-1,1] for EfficientNetV2) without needing Image.resize again.
        """
        t_pre = time.monotonic()
        logger.info("[ML] IMAGE SHAPE START bytes=%d", len(image_bytes))
        with Image.open(BytesIO(image_bytes)) as img:
            logger.info("[ML] IMAGE OPENED format=%s size=%s mode=%s", getattr(img, "format", None), img.size, img.mode)
            img   = ImageOps.exif_transpose(img).convert("RGB")
            logger.info("[ML] IMAGE CONVERTED size=%s", img.size)
            pixels = np.asarray(img, dtype=np.float32) / 255.0   # refusal [0,1]
            logger.info("[ML] PIXELS shape=%s range=[%.3f, %.3f]", pixels.shape, pixels.min(), pixels.max())
            img224 = img.resize((224, 224), Image.LANCZOS)
            img224_arr = np.asarray(img224, dtype=np.float32)   # model input raw
            logger.info("[ML] IMAGE 224 READY shape=%s range=[%.3f, %.3f] %.3fs", img224_arr.shape, img224_arr.min(), img224_arr.max(), time.monotonic() - t_pre)

        self._pixels_f01    = pixels
        self._preload_result = img224_arr
        return pixels, img224_arr

    # ─── Refusal detection ───────────────────────────────────────────────────

    def _refusal_first_pass(
        self, quality_check: QualityCheck, image_bytes: bytes,
    ) -> dict[str, object]:
        """Fast image-quality gate – refuse ONLY if image is invalid (blurry, too dark, etc.)."""
        if not quality_check.valid:
            logger.info("[Refusal] First pass: quality invalid, issues=%s", quality_check.issues)
            return {"refused": True, "reason": "image_non_exploitable"}
        
        # Preload pixels for prediction (used later)
        self._pixels_f01, self._preload_result = self._preload_for_prediction(image_bytes)
        
        # Accept all valid images - no green dominance check
        logger.info("[Refusal] First pass: quality valid, accepting")
        return {"refused": False, "reason": None}

    def _refusal_second_pass(
        self,
        quality_check:     QualityCheck,
        confidence_details: ConfidenceDetails | None = None,
    ) -> dict[str, object]:
        """Second-pass gate using ONLY confidence thresholds – no green dominance check.
        
        Refuse ONLY if prediction confidence is extremely low (quasi-random).
        """
        if confidence_details is None:
            return {"refused": False, "reason": None}
        
        # Refuse only if confidence is extremely low
        if confidence_details.max_prob < self.settings.refusal_min_confidence:
            logger.info("[Refusal] Second pass: max_prob=%.3f < %.3f (refusing)",
                       confidence_details.max_prob, self.settings.refusal_min_confidence)
            return {"refused": True, "reason": "confiance_trop_faible"}
        
        if confidence_details.margin < self.settings.refusal_min_margin:
            logger.info("[Refusal] Second pass: margin=%.3f < %.3f (refusing)",
                       confidence_details.margin, self.settings.refusal_min_margin)
            return {"refused": True, "reason": "confiance_trop_faible"}
        
        # Accept all other predictions (including those with green pixels, low contrast, etc.)
        logger.info("[Refusal] Second pass: confidence OK (max_prob=%.3f, margin=%.3f), accepting",
                   confidence_details.max_prob, confidence_details.margin)
        return {"refused": False, "reason": None}

    # Keep original signature for any external callers ─────────────────────────
    def refusal_detection(
        self,
        image_bytes:       bytes,
        quality_check:     QualityCheck,
        confidence_details: ConfidenceDetails | None = None,
    ) -> dict[str, object]:
        """Backward-compatible single-call refusal detector.
        
        Refuse ONLY if:
        1. Image quality is invalid (blurry, too dark, etc.)
        2. Confidence is extremely low (quasi-random prediction)
        """
        # Quality check
        if not quality_check.valid:
            logger.info("[Refusal] Image invalid: %s", quality_check.issues)
            return {"refused": True, "reason": "image_non_exploitable"}
        
        # Confidence check
        if confidence_details:
            if confidence_details.max_prob < self.settings.refusal_min_confidence:
                logger.info("[Refusal] Low confidence: max_prob=%.3f < %.3f",
                           confidence_details.max_prob, self.settings.refusal_min_confidence)
                return {"refused": True, "reason": "confiance_trop_faible"}
            if confidence_details.margin < self.settings.refusal_min_margin:
                logger.info("[Refusal] Low margin: margin=%.3f < %.3f",
                           confidence_details.margin, self.settings.refusal_min_margin)
                return {"refused": True, "reason": "confiance_trop_faible"}
        
        # Accept all other cases
        logger.info("[Refusal] No refusal reasons, accepting image")
        return {"refused": False, "reason": None}

    # ─── Prediction ───────────────────────────────────────────────────────────

    def _predict_probabilities(
        self, models: dict[str, list],
    ) -> dict[str, float]:
        """Run every loaded model on the same 224×224 pre-built array.

        Uses cached img_224 from _preload_for_prediction (already called in pass 1).
        """
        assert hasattr(self, "_preload_result") and self._preload_result is not None
        img_224 = self._preload_result

        total_model_count = sum(len(models.get(label, [])) for label in LABELS)
        if total_model_count <= 0:
            return {label: 0.0 for label in LABELS}

        predictions_by_label: dict[str, list[tuple[float, float]]] = {label: [] for label in LABELS}

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
                    prob = float(future.result())
                except Exception:
                    logger.exception("[ML] concurrent predict failed for label=%s", label)
                    prob = 0.0
                predictions_by_label[label].append((prob, weight))

        probabilities: dict[str, float] = {label: 0.0 for label in LABELS}
        for label in LABELS:
            values_and_weights = predictions_by_label.get(label, [])
            if not values_and_weights:
                continue

            values = [item[0] for item in values_and_weights]
            weights = [item[1] for item in values_and_weights]

            w_arr = np.asarray(weights, dtype=np.float32)
            if w_arr.sum() <= 0:
                w_arr = np.ones_like(w_arr)
            probabilities[label] = float(
                np.average(np.asarray(values, dtype=np.float32), weights=w_arr)
            )
            logger.debug("[ML]  label=%s  n_models=%d  prob=%.6f", label, len(values), probabilities[label])
        return probabilities

    def _predict_with_model(self, loaded: LoadedModel, img_224: np.ndarray) -> float:
        """Run a single model inference on a pre-built 224×224 float32 array."""
        import time as _time
        t_infer = _time.monotonic()
        logger.info("[ML] MODEL PREDICT START label=%s family=%s shape=%s", loaded.label, loaded.family, img_224.shape)
        # img_224 is H×W×3 float32 raw pixel values (0–255 range).
        # Each model's preprocess function converts it to the backend's expected
        # range (TF preprocess_input handles [-1,1] or [0,1] etc.).
        try:
            processed = loaded.preprocess(img_224)
            logger.info("[ML] PREPROCESS done shape=%s range=[%.3f, %.3f]", processed.shape, processed.min(), processed.max())
            batch = np.expand_dims(processed, axis=0)  # (1, 224, 224, 3)

            if loaded.backend == "tensorflow":
                logger.info("[ML] CALLING TENSORFLOW PREDICT")
                result = loaded.model.predict(batch, verbose=0)  # type: ignore[union-attr]
                prob = float(np.asarray(result).ravel()[0])
            else:
                import torch  # lazy – torch is an optional dependency
                tensor = torch.from_numpy(batch).permute(0, 3, 1, 2).float()
                with torch.no_grad():
                    out = loaded.model(tensor)
                prob = float(out.detach().cpu().numpy().ravel()[0])
            logger.info("[ML] MODEL PREDICT END label=%s elapsed=%.3fs prob=%.4f", loaded.label, _time.monotonic() - t_infer, prob)
            return prob
        except Exception as e:
            logger.exception("[ML] MODEL PREDICT FAILED label=%s error=%s", loaded.label, e)
            return 0.0

    def _select_prediction(self, probabilities: dict[str, float]) -> dict[str, str]:
        """Choose the highest-probability label per nutrient group."""
        return {
            f"{nutrient}_level": max(labels, key=lambda lbl: probabilities.get(lbl, 0.0))
            for nutrient, labels in NUTRIENTS.items()
        }

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
        nutrient_weights = {
            "K": {"K0": -24, "K1": -6, "K2": 8},
            "N": {"N0": -20, "N1": -5, "N2": 9},
            "P": {"P0": -30, "P1": 8},
        }
        score = 100.0
        for nutrient, labels in NUTRIENTS.items():
            values = np.array(
                [max(probabilities.get(lbl, 0.0), 0.0) for lbl in labels],
                dtype=np.float32,
            )
            if float(values.sum()) <= 0:
                continue
            weights = np.array(
                [nutrient_weights[nutrient][lbl] for lbl in labels],
                dtype=np.float32,
            )
            score += float(np.dot(values / values.sum(), weights))
        return int(max(0, min(100, round(score))))

    # ─── Advice ───────────────────────────────────────────────────────────────

    def generate_field_advice(
        self,
        prediction:    dict[str, str],
        probabilities: dict[str, float],
        score:         int,
        confidence:    float,
    ) -> tuple[str, str]:
        parts: list[str] = []

        p_lvl = prediction.get("P_level", "P1")
        n_lvl = prediction.get("N_level", "N1")
        k_lvl = prediction.get("K_level", "K1")

        if p_lvl == "P0":
            parts.append("Le phosphore semble insuffisant. Une fertilisation phosphatée modérée peut être envisagée après confirmation.")
        elif p_lvl == "P1":
            parts.append("Le phosphore paraît acceptable, avec un suivi régulier recommandé.")

        if n_lvl == "N0":
            parts.append("Le sol montre un signal azoté faible. Surveiller les besoins de croissance.")
        elif n_lvl == "N1":
            parts.append("L'azote est intermédiaire : maintenir un suivi de croissance et de vigueur.")

        if k_lvl == "K0":
            parts.append("Le potassium paraît faible. Vérifier les besoins hydriques et la fertilisation.")
        elif k_lvl == "K1":
            parts.append("Le potassium est intermédiaire : un suivi terrain reste pertinent.")

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
        if   status == "image_non_exploitable": return base + " Image non exploitable pour une décision fiable."
        if   confidence >= 0.80:                  return base + " Signal solide pour un pré-diagnostic terrain."
        elif confidence >= 0.60:                  return base + " Lecture utile, à confirmer selon le contexte parcellaire."
        return base + " Lecture exploratoire à confirmer par laboratoire."

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
        prediction = {"K_level": "K0", "N_level": "N0", "P_level": "P0"}
        agronomic_advice         = self.advice.build(NutrientPrediction(**prediction))
        confidence_details       = ConfidenceDetails(max_prob=0.0, second_prob=0.0, margin=0.0, top_label=None, top_group=None)  # type: ignore[call-arg]
        return {
            "analysis_id":           analysis_id,
            "model_name":            "SoilAI ML Ensemble",
            "prediction":            NutrientPrediction(**prediction),
            "confidence":            0.0,
            "status":                "image_non_exploitable",
            "can_trust_result":      False,
            "quality_check":         quality_check,
            "confidence_details":    confidence_details,
            "interpretation":        "L'image ne permet pas une lecture NPK fiable.",
            "recommendation":        "Reprendre une photo plus nette, bien éclairée et centrée sur le sol.",
            "agronomic_advice":      agronomic_advice,
            "field_advice":          "Impossible de fournir un conseil fiable avec cette image.",
            "field_disclaimer":      self.advice.field_disclaimer(),
            "warning_message":       "Cette image ne permet pas une estimation fiable du sol.",
            "recommendation_message":"Reprendre une photo plus nette, bien éclairée et centrée sur le sol.",
            "is_mock":               False,
            "timestamp":             datetime.now(timezone.utc),
            "source":                (f"uploaded_image:{user_id}" if user_id else "uploaded_image"),
            "model_status":          "model_ready",
            "probabilities":         {label: 0.0 for label in LABELS},
            "score":                 0,
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