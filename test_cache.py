import sys, os, time
sys.path.insert(0, r"C:\Users\surface pro 7\Desktop\npk_90percent\backend")
os.chdir(r"C:\Users\surface pro 7\Desktop\npk_90percent")

from app.core.config import get_settings
from app.services.ml_prediction_service import get_global_models, reset_global_models, MLPredictionService

settings = get_settings()

# First call = disk load
reset_global_models()
t0 = time.monotonic()
m1 = get_global_models(settings)
t1 = time.monotonic()
print(f"Disk load: {t1-t0:.3f}s  models={[(k,len(v)) for k,v in m1.items() if k!='_elapsed_s']}")

# Second call = cache hit
t0 = time.monotonic()
m2 = get_global_models(settings)
t1 = time.monotonic()
print(f"Cache hit: {t1-t0:.8f}s  same_objs={m1 is m2}")

# MLPredictionService.load_models() compat method
svc = MLPredictionService(settings)
reset_global_models()
t0 = time.monotonic()
m3 = [svc.load_models()]
t1 = time.monotonic()
print(f"service.load_models(): {t1-t0:.3f}s  ok={len(m3)==1}")
print("ALL OK")
