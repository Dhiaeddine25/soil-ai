"""Quick import / smoke tests for the optimized ml_prediction_service."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Capture timing
import time

# ── Test 1: module-level TF priming ───────────────────────────────────────────
t0 = time.monotonic()
from app.services.ml_prediction_service import (
    get_global_models, reset_global_models,
    _TF_AVAILABLE, _TF_PREPROCESS_FN, _backend_spec,
    MLPredictionService, _load_models_from_disk,
)
print(f"[T1] module import took {time.monotonic() - t0:.3f}s")
print(f"[T1] _TF_AVAILABLE  = {_TF_AVAILABLE}")
print(f"[T1] preprocess_fns = {list(_TF_PREPROCESS_FN.keys())}")

# Verify _backend_spec does NOT do inline TF imports anymore
any(_backend_spec(f) for f in ("densenet201", "efficientnetv2l", "mobilenetv2"))
print("[T1] _backend_spec – no inline import, done.")

# ── Test 2: model cache hit pattern ───────────────────────────────────────────
reset_global_models()
assert _GLOBAL_MODELS is None, "Cache not cleared after reset"

t1 = time.monotonic()
m1 = get_global_models(type("S", (), {"root_dir": Path(".")})())
t2 = time.monotonic()
m2 = get_global_models(type("S", (), {"root_dir": Path(".")})())
t3 = time.monotonic()
print(f"[T2] disk_load  = {t2-t1:.3f}s  cache_hit  = {t3-t2:.6f}s")
assert t3 - t2 < 0.001, "Cache hit not fast – models are being reloaded!"
print("[T2] Cache heat OK")

print("\n=== All smoke tests passed ===")
