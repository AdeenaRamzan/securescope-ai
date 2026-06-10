# backend/src/core/tokenizer.py
# Purpose: Convert raw Python code string into
#          padded sequence of token IDs
# Used by: BiLSTM model (Phase 2)

import tokenize
import io
import torch
from typing import List


def code_to_tokens(code: str) -> List[str]:
    """
    Convert Python code string to list of token strings.
    Uses Python's built-in tokenize module.
    
    Example:
        "def get_user(uid):" 
        -> ["def", "get_user", "(", "uid", ")", ":"]
    """
    tokens = []
    try:
        reader = io.StringIO(code).readline
        for tok in tokenize.generate_tokens(reader):
            if tok.string.strip():
                tokens.append(tok.string)
    except tokenize.TokenError:
        pass
    return tokens


def tokens_to_ids(tokens: List[str],
                  vocab: dict,
                  max_len: int = 256) -> List[int]:
    """
    Convert token strings to integer IDs using vocabulary.
    Pads or truncates to max_len.
    
    Unknown tokens map to <UNK> (ID=1)
    Padding uses <PAD> (ID=0)
    """
    ids = [vocab.get(tok, 1) for tok in tokens]  # 1 = <UNK>

    # Truncate if too long
    if len(ids) > max_len:
        ids = ids[:max_len]

    # Pad if too short
    while len(ids) < max_len:
        ids.append(0)  # 0 = <PAD>

    return ids


def code_to_tensor(code: str,
                   vocab: dict,
                   max_len: int = 256) -> torch.Tensor:
    """
    Full pipeline: code string -> PyTorch tensor
    Ready to feed into BiLSTM model.
    """
    tokens = code_to_tokens(code)
    ids    = tokens_to_ids(tokens, vocab, max_len)
    return torch.tensor(ids, dtype=torch.long).unsqueeze(0)