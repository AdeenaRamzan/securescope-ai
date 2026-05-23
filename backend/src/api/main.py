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
    threshold_used: float
    model_version:  str
    model_probs:    dict
    features_fired: list
    scan_time_ms:   float


# ── Health check endpoint ─────────────────────────
@app.get("/health")
def health_check():
    return {
        "status":  "healthy",
        "model":   "v3_ensemble",
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


# ── Root endpoint ─────────────────────────────────
@app.get("/")
def root():
    return {
        "name":        "SecureScope AI API",
        "version":     "1.0.0",
        "docs":        "/docs",
        "health":      "/health",
        "scan":        "POST /scan"
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
    print("Model warmup complete — API ready")