# Models

Most model weights are not stored in Git due to file size.

## Phase 1 — Ensemble

To reproduce:
1. Run `backend/notebooks/phase1_development.ipynb`
2. Models will be saved to this directory automatically

## Phase 2 — Binary BiLSTM

Required files:
- `bilstm_phase2_binary_best.pth`
- `vocabulary_phase2_binary_bilstm.json`
- `phase2_binary_bilstm_config.json`

To reproduce:
1. Run `backend/notebooks/phase2_bilstm.ipynb`
2. Holdout F1: **0.9505** on PyCode Vul test set

