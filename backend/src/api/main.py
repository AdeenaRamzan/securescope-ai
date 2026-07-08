# backend/src/api/main.py
# Purpose: FastAPI application
#          Exposes /scan endpoint for vulnerability detection
#          Loads models once at startup, serves predictions

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
import time

from src.core.predictor import predict
from src.core.predictor_phase2 import predict_bilstm
from src.core.phase3_pipeline import (
    load_phase3_resources,
    phase3_load_error,
    scan_deep_phase3,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    dummy_code = "def hello():\n    return 'world'"
    predict(dummy_code)
    predict_bilstm(dummy_code)
    logger.info("Phase 1/2 model warmup complete")

    load_phase3_resources()
    if phase3_load_error():
        logger.warning("Phase 3 unavailable: %s", phase3_load_error())
    yield
# ── App setup ─────────────────────────────────────
app = FastAPI(
    title="SecureScope AI",
    description="AI-powered Python code vulnerability scanner. "
                "Detects SQL injection, hardcoded secrets, "
                "insecure eval, path traversal, command injection.",
    version="1.0.0",
    lifespan=lifespan
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
    vulnerability_type: str
    danger:         str
    fix:            str
    owasp_ref:      str
    pipeline:       str
    llm:            str
    scan_time_ms:   float


def _risk_from_confidence(confidence: float, is_vulnerable: bool) -> str:
    if not is_vulnerable:
        return "SAFE"
    if confidence >= 0.85:
        return "HIGH"
    if confidence >= 0.65:
        return "MEDIUM"
    return "LOW"


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

# ── Phase 1 + Phase 2 cascade endpoint ────────────
@app.post("/scan/cascade", response_model=ScanResponse)
def scan_cascade(request: ScanRequest):
    """
    Phase 1 + Phase 2 cascade scan.
    Combines ensemble features with the BiLSTM sequence model.
    """
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Only Python supported"
        )

    try:
        start = time.time()
        phase1 = predict(request.code)
        phase2 = predict_bilstm(request.code)
        elapsed = round((time.time() - start) * 1000, 2)

        confidence = max(phase1["confidence"], phase2["confidence"])
        is_vulnerable = bool(phase1["is_vulnerable"] or phase2["is_vulnerable"])
        model_probs = {
            **phase1.get("model_probs", {}),
            **phase2.get("model_probs", {}),
        }

        return ScanResponse(
            is_vulnerable=is_vulnerable,
            confidence=confidence,
            risk_level=_risk_from_confidence(confidence, is_vulnerable),
            phase1_confidence=phase1["confidence"],
            phase2_confidence=phase2["confidence"],
            threshold_used=phase1.get("threshold_used", 0.55),
            model_version="phase1_phase2_cascade",
            model_probs=model_probs,
            features_fired=phase1.get("features_fired", []),
            scan_time_ms=elapsed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cascade prediction failed: {str(e)}"
        )


# ── Phase 3 deep endpoint ─────────────────────────
@app.post("/scan/deep", response_model=DeepScanResponse)
def scan_deep(request: ScanRequest):
    """
    Phase 3 deep scan.
    CodeBERT binary detection -> feature-based type identification
    -> OWASP FAISS retrieval -> Groq explanation.
    """
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Only Python supported"
        )

    try:
        start = time.time()
        result = scan_deep_phase3(request.code)
        logger.info(
            "Phase 3 /scan/deep endpoint %.2f ms",
            (time.time() - start) * 1000,
        )
        return DeepScanResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Phase 3 models are unavailable. {str(e)}"
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
