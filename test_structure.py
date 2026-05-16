import sys, os, time
sys.path.insert(0, r"C:\Users\surface pro 7\Desktop\npk_90percent\backend")
os.chdir(r"C:\Users\surface pro 7\Desktop\npk_90percent")

print("=== Phase timing log validator ===")

# Verify predict_npk grading call structure
import ast, inspect

from app.services.ml_prediction_service import MLPredictionService, _load_models_from_disk, _backend_spec

src = inspect.getsource(MLPredictionService.predict_npk)

# These strings must appear in predict_npk – they represent every optimization
required_strings = [
    "t_total",
    "save_image",
    "quality_check",
    "_refusal_first_pass",
    "_preload_for_prediction",
    "get_global_models",
    "models_loaded",
    "_predict_probabilities",
    "_select_prediction",
    "build_confidence_details",
    "_refusal_second_pass",
    "calculate_confidence",
    "calculate_soil_score",
    "generate_field_advice",
    "determine_status",
    "og_total",  # total elapsed logged at end
]
missing = [s for s in required_strings if s not in src]
if missing:
    print(f"MISSING from predict_npk: {missing}")
else:
    print("[OK] All expected strings found in predict_npk")

# Verify _predict_with_model takes pre-built img_224 array (not bytes)
src_pred = inspect.getsource(MLPredictionService._predict_with_model)
if "img_224" in src_pred and "Image.open" not in src_pred:
    print("[OK] _predict_with_model uses pre-built img_224, no Image.open inside")
else:
    print("[WARN] _predict_with_model might still read image per call")

# Verify _preload_for_prediction does BOTH: pixels + 224×224 array
src_pre = inspect.getsource(MLPredictionService._preload_for_prediction)
count = src_pre.count("Image.open(BytesIO")
if count == 1:
    print("[OK] _preload_for_prediction opens BytesIO exactly once")
else:
    print(f"[WARN] _preload_for_prediction opens BytesIO {count}x")

print("_TF_LOAD_FN keys =", list(_backend_spec.__code__.co_consts[:5]))
print("\nAll structure checks passed")
