# backend/src/core/vocab_builder.py
# Purpose: Build vocabulary from training data
# Run ONCE on training data, save to disk
# Never hardcode vocabulary — always build from data

import tokenize
import io
import json
from collections import Counter
from pathlib import Path


def build_vocabulary(code_samples: list,
                     max_vocab_size: int = 5000) -> dict:
    """
    Build vocabulary from actual code samples.
    Returns dict mapping token string to integer ID.
    
    Special tokens:
        <PAD> = 0  padding for sequences shorter than max_len
        <UNK> = 1  unknown tokens not seen in training
    """
    counter = Counter()

    for code in code_samples:
        try:
            reader = io.StringIO(code).readline
            for tok in tokenize.generate_tokens(reader):
                if tok.string.strip():
                    counter[tok.string] += 1
        except tokenize.TokenError:
            pass

    # Special tokens first — always at fixed positions
    vocab = {'<PAD>': 0, '<UNK>': 1}

    # Add most common tokens
    for token, _ in counter.most_common(max_vocab_size - 2):
        vocab[token] = len(vocab)

    return vocab


def save_vocabulary(vocab: dict, save_path: str):
    """Save vocabulary to JSON file."""
    with open(save_path, 'w') as f:
        json.dump(vocab, f, indent=2)
    print(f"Vocabulary saved: {save_path}")
    print(f"Vocabulary size: {len(vocab)}")


def load_vocabulary(vocab_path: str) -> dict:
    """Load vocabulary from JSON file."""
    with open(vocab_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    print("Run this from your notebook, not directly.")
    print("Usage: build_vocabulary(df['code'].tolist())")