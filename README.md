# 🛡️ SecureScope AI

<div align="center">

### AI-Powered Python Vulnerability Scanner

Detect vulnerable Python code using an ensemble of machine learning models trained on real-world security datasets.

<br/>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge)](https://securescope-ai.vercel.app)
[![API](https://img.shields.io/badge/API-HuggingFace-yellow?style=for-the-badge)](https://adeenaramzan93-securescope-ai-api.hf.space/docs)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## Overview

SecureScope AI scans Python functions for common security vulnerabilities before deployment.

Developers can paste Python code and instantly receive:

* Vulnerability detection
* Confidence scoring
* Risk classification
* Triggered security indicators
* API-based analysis results

### Supported Vulnerabilities

| Vulnerability                | Status |
| ---------------------------- | ------ |
| SQL Injection                | ✅      |
| Hardcoded Secrets            | ✅      |
| Insecure `eval()` / `exec()` | ✅      |
| Path Traversal               | ✅      |
| Command Injection            | ✅      |

---

## Live Demo

| Service  | URL                                                     |
| -------- | ------------------------------------------------------- |
| Frontend | https://securescope-ai.vercel.app                       |
| API Docs | https://adeenaramzan93-securescope-ai-api.hf.space/docs |

---

## Architecture

```mermaid id="m68g8q"
flowchart TD

    A["Python Code Input"]

    A --> B["Phase 1 Feature Extraction<br/>22 Static Features"]

    B --> C["ANN"]
    B --> D["XGBoost"]
    B --> E["LightGBM"]

    C --> F["Phase 1 Ensemble Score"]
    D --> F
    E --> F

    A --> G["Phase 2 Tokenization"]

    G --> H["BiLSTM Sequence Model"]

    F --> I["Cascade Decision Engine"]
    H --> I

    I --> J["Risk Classification<br/>SAFE / MEDIUM / HIGH"]

    J --> K["FastAPI Backend"]

    K --> L["Next.js Frontend"]

    style A fill:#1e1e2f,color:#fff,stroke:#00b4d8,stroke-width:2px
    style B fill:#252541,color:#fff,stroke:#7b2cbf,stroke-width:2px

    style C fill:#1b4332,color:#fff
    style D fill:#3c096c,color:#fff
    style E fill:#5f0f40,color:#fff

    style F fill:#14213d,color:#fff,stroke:#fca311,stroke-width:2px

    style G fill:#1d3557,color:#fff
    style H fill:#457b9d,color:#fff,stroke:#90e0ef,stroke-width:2px

    style I fill:#2b2d42,color:#fff,stroke:#ef233c,stroke-width:2px

    style J fill:#264653,color:#fff
    style K fill:#2a9d8f,color:#fff
    style L fill:#22223b,color:#fff
```


---

## Model Performance

Evaluated on **3,563 real held-out Python functions** from the PyCode Vul dataset.

### Phase 1 — Ensemble Features

| Metric    | Score     |
| --------- | --------- |
| Accuracy  | **73.4%** |
| Precision | 0.680     |
| Recall    | 0.773     |
| F1 Score  | **0.723** |
| Threshold | 0.39      |

### Phase 2 — Binary BiLSTM Sequence

| Metric    | Score      |
| --------- | ---------- |
| Accuracy  | **95.6%**  |
| Precision | 0.954      |
| Recall    | 0.947      |
| F1 Score  | **0.9505** |
| Threshold | 0.50       |

| Comparison | F1 Score |
| ---------- | -------- |
| Phase 1    | 0.723    |
| Phase 2    | **0.9505** |

> Performance metrics reflect real-world GitHub code rather than synthetic-only benchmarks.

---

## Dataset

| Source                   | Rows        | Description                      |
| ------------------------ | ----------- | -------------------------------- |
| PyCode Vul (IEEE 2025)   | 14,248      | Real GitHub vulnerable functions |
| Synthetic OWASP Examples | 2,750       | Hand-crafted verified samples    |
| **Total Training Data**  | **~17,000** | Combined dataset                 |
| Holdout Test Set         | 3,563       | Never used during training       |

---

## Feature Engineering

SecureScope extracts 22 static-analysis features from each Python function.

### Regex Features

* SQL concatenation patterns
* Hardcoded secret names
* `eval()` / `exec()` detection
* Shell command execution
* Path traversal indicators
* User input references
* Parameterized query detection

### AST Features

* Dangerous function call counts
* Sensitive variable assignments
* Unsafe deserialization usage

### Structural Features

* Nesting depth
* Parameter count
* Exception handling patterns
* Network operations
* Weak cryptography usage

---

## Tech Stack

| Layer                 | Technologies                        |
| --------------------- | ----------------------------------- |
| ML Models             | TensorFlow/Keras, XGBoost, LightGBM, PyTorch BiLSTM |
| Feature Extraction    | Python AST, Regex                   |
| Backend API           | FastAPI, Uvicorn, Pydantic          |
| Frontend              | React, Next.js, Tailwind CSS        |
| Deployment            | Docker, HuggingFace Spaces, Vercel  |
| Hyperparameter Tuning | Keras Tuner                         |

---

## Detection Pipeline

```text id="u5yh6g"
Python Code
    ↓
Feature Extraction
    ↓
Ensemble ML Models
    ↓
Soft Voting
    ↓
Risk Classification
    ↓
REST API Response
    ↓
Frontend Visualization
```

---

## Project Philosophy

This project focuses on end-to-end AI engineering and deployment rather than acting as a production security product.

Key areas demonstrated:

* Ensemble ML system design
* Static analysis pipelines
* Real-world evaluation methodology
* API deployment architecture
* Dockerized ML services
* Frontend/backend AI integration

---

## Known Limitations

* Limited to 5 vulnerability categories
* Phase 1 feature engineering ceiling around ~77% F1 (Phase 2 BiLSTM addresses this)
* BiLSTM covers binary safe/vulnerable classification only (no per-vulnerability labels yet)
* HuggingFace free tier cold starts may delay first response

---

## Roadmap

* [x] Phase 1 — Ensemble ML + Feature Engineering
* [x] Phase 2 — BiLSTM Token Sequence Analysis
* [ ] Phase 3 — RAG + LLM Vulnerability Explanations
* [ ] Phase 4 — GitHub PR Review Bot
* [ ] Phase 5 — Multi-language Support

---

## Run Locally

### Clone Repository

```bash id="7j4m9n"
git clone https://github.com/AdeenaRamzan/securescope-ai

cd securescope-ai
```

### Backend Setup

```bash id="r4y0lb"
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

uvicorn src.api.main:app --reload --port 8000
```

### Frontend Setup

```bash id="m9tnul"
cd frontend

npm install

npm run dev
```

---

## Docker Deployment

```bash id="7wdrg8"
docker build -t securescope-ai .

docker run -p 8000:8000 securescope-ai
```

---

## Citation

```bibtex id="fcjlwm"
@dataset{pycodevul2025,
  title={PyCode Vul: A Python-based Software Vulnerability Dataset},
  author={Karim, Tasmin and Akter, Mst Shapna and Cuzzocrea, Alfredo},
  year={2025},
  publisher={IEEE}
}
```

---

## Author

**Adeena Ramzan**
AI Engineering Portfolio Project — 2026

Focused on:

* AI Security Engineering
* Machine Learning Systems
* Backend AI Infrastructure
* Full-Stack AI Deployment

---
