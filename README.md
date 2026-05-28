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

    A["Python Code Input"] --> B["Feature Extractor<br/>22 Features (Regex + AST)"]

    B --> C["ANN<br/>TensorFlow / Keras"]
    B --> D["XGBoost"]
    B --> E["LightGBM"]

    C --> F["Soft Voting<br/>Average Prediction Probabilities"]
    D --> F
    E --> F

    F --> G["Risk Classification<br/>HIGH / MEDIUM / LOW / SAFE / INCONCLUSIVE"]

    G --> H["FastAPI REST API"]
    H --> I["React Frontend"]

    style A fill:#1e1e2f,color:#fff,stroke:#00b4d8,stroke-width:2px
    style B fill:#252541,color:#fff,stroke:#7b2cbf,stroke-width:2px
    style C fill:#1b4332,color:#fff,stroke:#2d6a4f,stroke-width:2px
    style D fill:#3c096c,color:#fff,stroke:#5a189a,stroke-width:2px
    style E fill:#5f0f40,color:#fff,stroke:#9a031e,stroke-width:2px
    style F fill:#14213d,color:#fff,stroke:#fca311,stroke-width:2px
    style G fill:#2b2d42,color:#fff,stroke:#ef233c,stroke-width:2px
    style H fill:#264653,color:#fff,stroke:#2a9d8f,stroke-width:2px
    style I fill:#22223b,color:#fff,stroke:#4ea8de,stroke-width:2px
```

---

## Model Performance

Evaluated on **3,563 real held-out Python functions** from the PyCode Vul dataset.

| Metric    | Score     |
| --------- | --------- |
| Accuracy  | **73.4%** |
| Precision | 0.680     |
| Recall    | 0.773     |
| F1 Score  | **0.723** |
| Threshold | 0.39      |

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
| ML Models             | TensorFlow/Keras, XGBoost, LightGBM |
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
* Feature engineering ceiling around ~77% F1
* No sequence-based semantic understanding yet
* HuggingFace free tier cold starts may delay first response

---

## Roadmap

* [x] Phase 1 — Ensemble ML + Feature Engineering
* [ ] Phase 2 — BiLSTM Token Sequence Analysis
* [ ] Phase 3 — RAG + LLM Vulnerability Explanations
* [ ] Phase 4 — GitHub PR Review Bot
* [ ] Phase 5 — Multi-language Support

---

## Run Locally

### Clone Repository

```bash id="7j4m9n"
git clone https://github.com/AdeenaRamzan93/securescope-ai

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
