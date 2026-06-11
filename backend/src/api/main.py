# backend/src/api/main.py
# Purpose: FastAPI application
#          Exposes /scan endpoint for vulnerability detection
#          Loads models once at startup, serves predictions

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
import time

from src.core.predictor import predict
from src.core.predictor_phase2 import predict_bilstm
# ── App setup ─────────────────────────────────────
app = FastAPI(
    title="SecureScope AI",
    description="AI-powered Python code vulnerability scanner. "
                "Detects SQL injection, hardcoded secrets, "
                "insecure eval, path traversal, command injection.",
    version="1.0.0"
)

# ── CORS — allows React frontend to call this API ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── Request model ─────────────────────────────────
class ScanRequest(BaseModel):
    code: str
    language: Optional[str] = "python"

    @field_validator("code")
    @classmethod
    def code_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Code cannot be empty")
        if len(v) > 50000:
            raise ValueError("Code too long — maximum 50,000 characters")
        return v


# ── Response model ────────────────────────────────
class ScanResponse(BaseModel):
    is_vulnerable:  bool
    confidence:     float
    risk_level:     str
    phase1_confidence: float = 0.0
    phase2_confidence: float = 0.0
    threshold_used: float
    model_version:  str
    model_probs:    dict
    features_fired: list
    scan_time_ms:   float


class BiLSTMScanResponse(BaseModel):
    is_vulnerable:  bool
    confidence:     float
    risk_level:     str
    phase1_confidence: float = 0.0
    phase2_confidence: float = 0.0
    threshold_used: float
    model_version:  str
    model_name:     str
    model_probs:    dict
    sequence:       dict
    features_fired: list
    scan_time_ms:   float


class DeepScanResponse(BaseModel):
    is_vulnerable:  bool
    confidence:     float
    risk_level:     str
    phase1_confidence: float
    phase2_confidence: float
    model_version:  str
    features_fired: list
    scan_time_ms:   float


# ── Health check endpoint ─────────────────────────
@app.get("/health")
def health_check():
    return {
        "status":  "healthy",
        "model":   "v3_ensemble",
        "phase2":  "binary_bilstm",
        "version": "1.0.0"
    }


# ── Main scan endpoint ────────────────────────────
@app.post("/scan", response_model=ScanResponse)
def scan_code(request: ScanRequest):
    """
    Scan Python code for vulnerabilities.

    Send POST request with:
    {
        "code": "your python code here"
    }

    Returns prediction with confidence, risk level,
    which features fired, and individual model probabilities.
    """

    # Only Python supported in Phase 1
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Only Python is supported in Phase 1"
        )

    try:
        start = time.time()
        result = predict(request.code)
        elapsed = round((time.time() - start) * 1000, 2)

        return ScanResponse(
            is_vulnerable  = result["is_vulnerable"],
            confidence     = result["confidence"],
            risk_level     = result["risk_level"],
            phase1_confidence = result["confidence"],
            phase2_confidence = 0.0,
            threshold_used = result["threshold_used"],
            model_version  = result["model_version"],
            model_probs    = result["model_probs"],
            features_fired = result["features_fired"],
            scan_time_ms   = elapsed
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

# ── Phase 2 BiLSTM endpoint ───────────────────────
@app.post("/scan/bilstm", response_model=BiLSTMScanResponse)
def scan_bilstm(request: ScanRequest):
    """
    Phase 2 BiLSTM scan.
    Uses token sequences instead of hand-crafted features.
    More accurate than /scan for real production code.
    """
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Only Python supported"
        )
    try:
        start = time.time()
        result = predict_bilstm(request.code)
        elapsed = round((time.time() - start) * 1000, 2)

        return BiLSTMScanResponse(
            is_vulnerable      = result["is_vulnerable"],
            confidence         = result["confidence"],
            risk_level         = result["risk_level"],
            phase1_confidence  = 0.0,
            phase2_confidence  = result["confidence"],
            threshold_used     = result["threshold_used"],
            model_version      = result["model_version"],
            model_name         = result["model_name"],
            model_probs        = result["model_probs"],
            sequence           = result["sequence"],
            features_fired     = result["features_fired"],
            scan_time_ms       = elapsed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"BiLSTM prediction failed: {str(e)}"
        )

# ── Combined cascade endpoint ─────────────────────
@app.post("/scan/deep", response_model=DeepScanResponse)
def scan_deep(request: ScanRequest):
    """
    Cascade: Phase 1 ANN gate → Phase 2 BiLSTM confirmation
    Best accuracy for on-demand scanning.
    """
    if request.language.lower() != "python":
        raise HTTPException(status_code=400,
                           detail="Only Python supported")
    try:
        start = time.time()

        # Phase 1 — fast gate
        p1 = predict(request.code)

        # Phase 2 — BiLSTM confirmation
        p2 = predict_bilstm(request.code)

        # Combine — both must agree to flag HIGH
        ensemble_confidence = (
            p1["confidence"] * 0.4 +
            p2["confidence"] * 0.6  # BiLSTM weighted higher
        )

        is_vulnerable = p2["is_vulnerable"]  # BiLSTM is final word

        if not is_vulnerable:
            risk = "SAFE"
        elif ensemble_confidence >= 0.85:
            risk = "HIGH"
        elif ensemble_confidence >= 0.65:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        elapsed = round((time.time() - start) * 1000, 2)

        return {
            "is_vulnerable":      is_vulnerable,
            "confidence":         round(ensemble_confidence, 4),
            "risk_level":         risk,
            "phase1_confidence":  p1["confidence"],
            "phase2_confidence":  p2["confidence"],
            "model_version":      "cascade_p1_p2",
            "features_fired":     p1.get("features_fired", []),
            "scan_time_ms":       elapsed
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deep scan failed: {str(e)}"
        )
# ── Root endpoint ─────────────────────────────────
@app.get("/")
def root():
    return {
        "name":        "SecureScope AI API",
        "version":     "1.0.0",
        "docs":        "/docs",
        "health":      "/health",
        "scan":        "POST /scan",
        "scan_bilstm": "POST /scan/bilstm",
        "scan_deep":   "POST /scan/deep"
    }

    # ── Startup warmup ────────────────────────────────
@app.on_event("startup")
async def warmup():
    """
    Run a dummy prediction at startup so first
    real request is not slow due to TF warmup
    """
    dummy_code = "def hello():\n    return 'world'"
    predict(dummy_code)
    predict_bilstm(dummy_code)
    print("Model warmup complete — API ready")


