# backend/src/core/predictor.py
# Purpose: Load all 3 models + scaler at startup
#          Run ensemble prediction on extracted features
#          Return structured result for FastAPI

import json
import numpy as np
import joblib
import tensorflow as tf
from pathlib import Path
from typing import Dict

from src.core.feature_extractor import extract_features, FEATURE_NAMES


# ── Paths ─────────────────────────────────────────
MODELS_DIR = Path(__file__).resolve().parents[2] / "models" / "saved"


# ── Load everything once at startup ──────────────
print("Loading models...")

try:
    ANN_MODEL   = tf.keras.models.load_model(MODELS_DIR / "ann_v3_tuned.keras")
    XGB_MODEL   = joblib.load(MODELS_DIR / "xgb_v3.pkl")
    LGB_MODEL   = joblib.load(MODELS_DIR / "lgb_v3.pkl")
    SCALER      = joblib.load(MODELS_DIR / "scaler_v3.pkl")

    with open(MODELS_DIR / "ensemble_config.json") as f:
        CONFIG = json.load(f)

    THRESHOLD = CONFIG["deployment"]["threshold"]
# Override threshold to reduce false positives on simple code
    THRESHOLD = max(THRESHOLD, 0.55)
    print(f"All models loaded. Threshold: {THRESHOLD}")

except Exception as e:
    raise RuntimeError(f"Failed to load models: {e}")


# ── Risk level helper ─────────────────────────────
def get_risk_level(confidence: float, is_vulnerable: bool) -> str:
    if not is_vulnerable:
        if confidence < 0.45:
            return "SAFE"
        return "INCONCLUSIVE"
    if confidence >= 0.85:
        return "HIGH"
    if confidence >= 0.65:
        return "MEDIUM"
    return "LOW"


# ── Main prediction function ──────────────────────
def predict(code: str) -> Dict:
    """
    Takes raw Python code string.
    Returns prediction dict with all details.
    """

    # Step 1 — Extract 22 features
    features = extract_features(code)
    features_array = np.array(features).reshape(1, -1)

    # Step 2 — Scale for ANN (ANN needs scaled input)
    features_scaled = SCALER.transform(features_array)

    # Step 3 — Get probability from each model
    ann_prob = float(
        ANN_MODEL.predict(features_scaled, verbose=0)[0][0]
    )
    xgb_prob = float(
        XGB_MODEL.predict_proba(features_array)[0][1]
    )
    lgb_prob = float(
        LGB_MODEL.predict_proba(features_array)[0][1]
    )

    # Step 4 — Soft voting ensemble
    ensemble_prob = (ann_prob + xgb_prob + lgb_prob) / 3

    # Step 5 — Apply threshold
    is_vulnerable = ensemble_prob >= THRESHOLD

# Step 6 — Check specific vulnerability features
    specific_vuln_features = [
        features[0],   # f1_sql_concat
        features[1],   # f2_hardcoded_secret
        features[2],   # f3_eval_exec
        features[3],   # f4_path_traversal
        features[4],   # f5_cmd_injection
        features[10],  # f11_ast_dangerous_calls
        features[11],  # f12_ast_hardcoded_assign
    ]

    no_specific_features = all(f == 0 for f in specific_vuln_features)

    # If no specific vulnerability pattern fired → force SAFE
    if no_specific_features:
        return {
            "is_vulnerable":  False,
            "confidence":     round(ensemble_prob, 4),
            "risk_level":     "SAFE",
            "threshold_used": THRESHOLD,
            "model_version":  CONFIG["version"],
            "model_probs": {
                "ann":      round(ann_prob, 4),
                "xgboost":  round(xgb_prob, 4),
                "lightgbm": round(lgb_prob, 4)
            },
            "features_fired": []
        }

    # Step 7 — Apply threshold and build result
    deterministic_signal = not no_specific_features
    is_vulnerable = ensemble_prob >= THRESHOLD or deterministic_signal
    confidence = max(ensemble_prob, 0.95) if deterministic_signal else ensemble_prob

    result = {
        "is_vulnerable":  bool(is_vulnerable),
        "confidence":     round(confidence, 4),
        "risk_level":     get_risk_level(confidence, is_vulnerable),
        "threshold_used": THRESHOLD,
        "model_version":  CONFIG["version"],
        "model_probs": {
            "ann":      round(ann_prob, 4),
            "xgboost":  round(xgb_prob, 4),
            "lightgbm": round(lgb_prob, 4)
        },
        "features_fired": [
            name for name, val in zip(FEATURE_NAMES, features)
            if val > 0
        ]
    }

    return result
