# backend/src/models/bilstm_classifier.py
# Purpose: BiLSTM model architecture for Phase 2
# Input:   padded token sequence (batch_size, seq_len)
# Output:  6-class logits (batch_size, 6)
# Classes: 0=safe, 1=sql_injection, 2=hardcoded_secret,
#          3=insecure_eval, 4=path_traversal, 5=cmd_injection

import torch
import torch.nn as nn


CLASS_NAMES = [
    'safe',
    'sql_injection',
    'hardcoded_secret',
    'insecure_eval',
    'path_traversal',
    'cmd_injection'
]


class VulnerabilityBiLSTM(nn.Module):

    def __init__(self,
                 vocab_size: int,
                 embed_dim: int = 64,
                 hidden_dim: int = 128,
                 num_classes: int = 6,
                 num_layers: int = 2,
                 dropout: float = 0.3):
        super().__init__()

        # Embedding: token ID -> dense vector
        # padding_idx=0 means <PAD> tokens contribute nothing
        self.embedding = nn.Embedding(
            vocab_size, embed_dim, padding_idx=0
        )

        # Bidirectional LSTM
        # reads code left-to-right AND right-to-left
        # captures: what came before AND what comes after
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )

        # Classifier head
        # hidden_dim*2 because bidirectional
        # (forward hidden + backward hidden concatenated)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x shape: (batch_size, seq_len)
        output shape: (batch_size, num_classes)
        """
        # Token IDs -> embeddings
        emb = self.embedding(x)
        # emb shape: (batch_size, seq_len, embed_dim)

        # LSTM forward pass
        _, (hidden, _) = self.lstm(emb)
        # hidden shape: (num_layers*2, batch_size, hidden_dim)
        # [-2] = last layer forward direction
        # [-1] = last layer backward direction

        # Concatenate final states from both directions
        final = torch.cat([hidden[-2], hidden[-1]], dim=1)
        # final shape: (batch_size, hidden_dim*2)

        # Classify
        return self.classifier(final)
        # output shape: (batch_size, num_classes)