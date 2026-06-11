# backend/src/core/predictor_phase2.py
# Purpose: Load BiLSTM model and run prediction
# Used by: FastAPI /scan/bilstm endpoint

import torch
import torch.nn as nn
import json
import tokenize
import io
from pathlib import Path
from typing import Dict

# ── Paths ─────────────────────────────────────────
MODELS_DIR = Path(__file__).resolve().parents[2] / "models" / "saved"

# ── BiLSTM Architecture ───────────────────────────
class VulnerabilityBiLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=128,
                 hidden_dim=128, num_layers=2, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        emb = self.embedding(x)
        _, (hidden, _) = self.lstm(emb)
        final = torch.cat([hidden[-2], hidden[-1]], dim=1)
        return self.classifier(final)

# ── Load models at startup ────────────────────────
print("Loading Phase 2 BiLSTM...")

try:
    # Load vocabulary
    with open(MODELS_DIR / "vocabulary_phase2_binary_bilstm.json") as f:
        VOCAB = json.load(f)

    # Load config
    with open(MODELS_DIR / "phase2_binary_bilstm_config.json") as f:
        CONFIG = json.load(f)

    VOCAB_SIZE = len(VOCAB)
    MAX_LEN    = CONFIG.get("max_len", 256)
    THRESHOLD  = CONFIG.get("threshold", 0.5)

    # Load model
    BILSTM_MODEL = VulnerabilityBiLSTM(
    vocab_size=VOCAB_SIZE,
    embed_dim=CONFIG["embedding_dim"],
    hidden_dim=CONFIG["hidden_dim"],
    num_layers=CONFIG["num_layers"],
    dropout=CONFIG["dropout"]
    )
    BILSTM_MODEL.load_state_dict(
        torch.load(
            MODELS_DIR / "bilstm_phase2_binary_best.pth",
            map_location=torch.device("cpu")
        )
    )
    BILSTM_MODEL.eval()
    print(f"BiLSTM loaded. Vocab: {VOCAB_SIZE} | Max len: {MAX_LEN}")

except Exception as e:
    raise RuntimeError(f"Failed to load Phase 2 models: {e}")

# ── Tokenizer ─────────────────────────────────────
def code_to_tensor(code: str, max_len: int = 256) -> torch.Tensor:
    tokens = []
    try:
        reader = io.StringIO(code).readline
        for tok in tokenize.generate_tokens(reader):
            if tok.string.strip():
                tokens.append(tok.string)
    except tokenize.TokenError:
        pass

    ids = [VOCAB.get(tok, 1) for tok in tokens]
    ids = ids[:max_len]
    while len(ids) < max_len:
        ids.append(0)

    return torch.tensor(ids, dtype=torch.long).unsqueeze(0)

# ── Prediction function ───────────────────────────
def predict_bilstm(code: str) -> Dict:
    tensor = code_to_tensor(code, MAX_LEN)

    with torch.no_grad():
        logits = BILSTM_MODEL(tensor)
        vuln_prob = float(torch.sigmoid(logits).item())

    is_vulnerable = vuln_prob >= THRESHOLD

    if not is_vulnerable:
        risk = "SAFE"
    elif vuln_prob >= 0.85:
        risk = "HIGH"
    elif vuln_prob >= 0.65:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "is_vulnerable":  is_vulnerable,
        "confidence":     round(vuln_prob, 4),
        "risk_level":     risk,
        "threshold_used": THRESHOLD,
        "model_version":  CONFIG.get("phase", "Phase 2 Official"),
        "model_name":     CONFIG.get("model_name", "bilstm_phase2_binary"),
        "model_probs": {
            "bilstm": round(vuln_prob, 4),
        },
        "sequence": {
            "max_len": MAX_LEN,
            "vocab_size": VOCAB_SIZE,
        },
        "features_fired": []
    }
