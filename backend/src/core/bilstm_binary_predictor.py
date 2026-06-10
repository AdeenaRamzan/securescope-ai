# backend/src/core/bilstm_binary_predictor.py
# Purpose: Load the Phase 2 binary BiLSTM and run sequence-based inference.

import json
from pathlib import Path
from typing import Dict

import torch
import torch.nn as nn

from src.core.tokenizer import code_to_tensor


MODELS_DIR = Path(__file__).resolve().parents[2] / "models" / "saved"


class BinaryVulnerabilityBiLSTM(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embed_dim,
            padding_idx=0,
        )

        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        _, (hidden, _) = self.lstm(emb)
        final_hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)
        return self.classifier(final_hidden).squeeze(1)


def _risk_level(probability: float, is_vulnerable: bool) -> str:
    if not is_vulnerable:
        if probability < 0.30:
            return "SAFE"
        return "INCONCLUSIVE"
    if probability >= 0.85:
        return "HIGH"
    if probability >= 0.65:
        return "MEDIUM"
    return "LOW"


print("Loading Phase 2 BiLSTM...")

try:
    with open(MODELS_DIR / "phase2_binary_bilstm_config.json") as f:
        BILSTM_CONFIG = json.load(f)

    with open(MODELS_DIR / "vocabulary_phase2_binary_bilstm.json") as f:
        BILSTM_VOCAB = json.load(f)

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    BILSTM_THRESHOLD = float(BILSTM_CONFIG.get("threshold", 0.5))
    BILSTM_MAX_LEN = int(BILSTM_CONFIG.get("max_len", 512))

    BILSTM_MODEL = BinaryVulnerabilityBiLSTM(
        vocab_size=len(BILSTM_VOCAB),
        embed_dim=int(BILSTM_CONFIG.get("embedding_dim", 128)),
        hidden_dim=int(BILSTM_CONFIG.get("hidden_dim", 128)),
        num_layers=int(BILSTM_CONFIG.get("num_layers", 2)),
        dropout=float(BILSTM_CONFIG.get("dropout", 0.3)),
    ).to(DEVICE)

    state_dict = torch.load(
        MODELS_DIR / "bilstm_phase2_binary_best.pth",
        map_location=DEVICE,
    )
    BILSTM_MODEL.load_state_dict(state_dict)
    BILSTM_MODEL.eval()

    print(
        "Phase 2 BiLSTM loaded. "
        f"Vocab size: {len(BILSTM_VOCAB)}, threshold: {BILSTM_THRESHOLD}"
    )

except Exception as e:
    raise RuntimeError(f"Failed to load Phase 2 BiLSTM: {e}")


def predict_bilstm_binary(code: str) -> Dict:
    """
    Takes raw Python code and returns Phase 2 binary BiLSTM prediction.
    """
    x = code_to_tensor(code, BILSTM_VOCAB, max_len=BILSTM_MAX_LEN).to(DEVICE)

    with torch.no_grad():
        logit = BILSTM_MODEL(x)
        probability = float(torch.sigmoid(logit)[0].cpu().item())

    is_vulnerable = probability >= BILSTM_THRESHOLD

    return {
        "is_vulnerable": bool(is_vulnerable),
        "confidence": round(probability, 4),
        "risk_level": _risk_level(probability, is_vulnerable),
        "threshold_used": BILSTM_THRESHOLD,
        "model_version": BILSTM_CONFIG.get("phase", "Phase 2 Official"),
        "model_name": BILSTM_CONFIG.get("model_name", "BinaryVulnerabilityBiLSTM"),
        "model_probs": {
            "bilstm": round(probability, 4),
        },
        "sequence": {
            "max_len": BILSTM_MAX_LEN,
            "vocab_size": len(BILSTM_VOCAB),
        },
    }
