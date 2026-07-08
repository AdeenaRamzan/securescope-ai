# backend/src/core/phase3_pipeline.py
# Purpose: Phase 3 CodeBERT + OWASP RAG + Groq explanation pipeline.

import logging
import os
import pickle
import time
import ast
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from src.core.feature_extractor import FEATURE_NAMES, extract_features


LOGGER = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parents[2] / "models" / "saved"
CODEBERT_DIR = MODELS_DIR / "codebert_binary"
CODEBERT_THRESHOLD = 0.23
CODEBERT_MAX_LEN = 512
GROQ_MODEL = "llama-3.1-8b-instant"

_resources: Dict = {}
_load_error: Optional[str] = None


TYPE_QUERIES = {
    "sql_injection": (
        "SQL injection prevention parameterized queries prepared statements "
        "user input database query"
    ),
    "hardcoded_secret": (
        "hardcoded secrets API keys passwords tokens secret management "
        "credential storage"
    ),
    "insecure_eval": (
        "unsafe eval exec code execution deserialization remote code execution "
        "prevention"
    ),
    "path_traversal": (
        "path traversal directory traversal file path validation user supplied "
        "filename"
    ),
    "cmd_injection": (
        "OS command injection prevention avoid shell execution subprocess "
        "user input"
    ),
    "unknown": "general secure coding input validation secure code review",
}

SQL_KEYWORDS = ("SELECT", "INSERT", "UPDATE", "DELETE", "WHERE", "ORDER BY")
SQL_SINKS = {"execute", "executemany", "query", "raw"}
PATH_SINKS = {"open"}
PATH_HINTS = ("path", "file", "filename", "dir", "directory")


def _risk_level(confidence: float, is_vulnerable: bool) -> str:
    if not is_vulnerable:
        return "SAFE"
    if confidence >= 0.85:
        return "HIGH"
    if confidence >= 0.65:
        return "MEDIUM"
    return "LOW"


def _encode_code_head_tail(code: str, tokenizer) -> Dict:
    encoded = tokenizer(
        str(code),
        add_special_tokens=False,
        truncation=False,
    )

    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]
    content_len = CODEBERT_MAX_LEN - 2

    if len(input_ids) > content_len:
        head_len = content_len // 2
        tail_len = content_len - head_len
        input_ids = input_ids[:head_len] + input_ids[-tail_len:]
        attention_mask = attention_mask[:head_len] + attention_mask[-tail_len:]

    input_ids = [tokenizer.cls_token_id] + input_ids + [tokenizer.sep_token_id]
    attention_mask = [1] + attention_mask + [1]

    padding_len = CODEBERT_MAX_LEN - len(input_ids)
    input_ids += [tokenizer.pad_token_id] * padding_len
    attention_mask += [0] * padding_len

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
    }


def load_phase3_resources() -> None:
    """
    Load all Phase 3 resources once during app startup.
    Leaves a load error instead of crashing the app, so existing endpoints
    continue to work.
    """
    global _load_error

    if _resources:
        return

    start = time.perf_counter()
    try:
        import torch
        from groq import Groq
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set.")

        LOGGER.info("Loading Phase 3 CodeBERT tokenizer/model")
        LOGGER.info("CodeBERT tokenizer path: %s", CODEBERT_DIR)
        tokenizer = AutoTokenizer.from_pretrained(
            CODEBERT_DIR,
            local_files_only=True,
        )
        LOGGER.info("CodeBERT model path: %s", CODEBERT_DIR)
        model = AutoModelForSequenceClassification.from_pretrained(
            CODEBERT_DIR,
            num_labels=2,
            local_files_only=True,
        )
        LOGGER.info("CodeBERT config num_labels: %s", model.config.num_labels)
        LOGGER.info("CodeBERT config id2label: %s", model.config.id2label)
        LOGGER.info("CodeBERT config label2id: %s", model.config.label2id)

        model.eval()

        LOGGER.info("Loading OWASP metadata")
        with open(MODELS_DIR / "owasp_metadata.pkl", "rb") as f:
            metadata = pickle.load(f)

        groq_client = Groq(api_key=groq_api_key)

        _resources.update(
            {
                "torch": torch,
                "tokenizer": tokenizer,
                "codebert": model,
                "metadata": metadata,
                "groq": groq_client,
            }
        )
        _load_error = None
        LOGGER.info(
            "Phase 3 resources loaded in %.2f ms",
            (time.perf_counter() - start) * 1000,
        )

    except Exception as exc:
        _resources.clear()
        _load_error = str(exc)
        LOGGER.exception("Phase 3 resources unavailable: %s", exc)


def phase3_available() -> bool:
    return bool(_resources)


def phase3_load_error() -> Optional[str]:
    return _load_error


def _predict_codebert_binary(code: str) -> Dict:
    torch = _resources["torch"]
    tokenizer = _resources["tokenizer"]
    model = _resources["codebert"]

    encoded = _encode_code_head_tail(code, tokenizer)
    inputs = {
        "input_ids": torch.tensor([encoded["input_ids"]], dtype=torch.long),
        "attention_mask": torch.tensor([encoded["attention_mask"]], dtype=torch.long),
    }

    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=1)
        predicted_class = int(torch.argmax(probabilities, dim=1)[0].item())
        probability = float(probabilities[0][1].item())

    LOGGER.info("CodeBERT raw logits: %s", logits.detach().cpu().tolist())
    LOGGER.info("CodeBERT softmax probabilities: %s", probabilities.detach().cpu().tolist())
    LOGGER.info("CodeBERT predicted class argmax: %s", predicted_class)
    LOGGER.info("CodeBERT confidence probability used: %.8f", probability)

    return {
        "is_vulnerable": probability >= CODEBERT_THRESHOLD,
        "confidence": probability,
    }


def _contains_sql_keyword(value: str) -> bool:
    upper = value.upper()
    return any(keyword in upper for keyword in SQL_KEYWORDS)


def _expr_has_concat(node: ast.AST) -> bool:
    return any(isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add) for child in ast.walk(node))


def _expr_has_name(node: ast.AST, names: set) -> bool:
    return any(isinstance(child, ast.Name) and child.id in names for child in ast.walk(node))


def _expr_has_sql_literal(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Constant)
        and isinstance(child.value, str)
        and _contains_sql_keyword(child.value)
        for child in ast.walk(node)
    )


def _detect_sql_injection_flow(code: str) -> bool:
    """
    Catch common SQL injection flow that the original 22-feature extractor can miss:
    SQL text is stored in one variable, concatenated into another, then passed to
    cursor.execute/db.query/raw.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    sql_vars = set()
    unsafe_sql_vars = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if not targets:
                continue

            has_sql = _expr_has_sql_literal(node.value) or _expr_has_name(node.value, sql_vars)
            has_concat = _expr_has_concat(node.value)
            has_unsafe_sql = _expr_has_name(node.value, unsafe_sql_vars)

            if has_sql:
                sql_vars.update(targets)
            if (has_sql and has_concat) or (has_unsafe_sql and has_concat):
                unsafe_sql_vars.update(targets)

        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
            if node.target.id in sql_vars and isinstance(node.op, ast.Add):
                unsafe_sql_vars.add(node.target.id)

    if not unsafe_sql_vars:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name not in SQL_SINKS:
            continue

        for arg in node.args:
            if isinstance(arg, ast.Name) and arg.id in unsafe_sql_vars:
                return True
            if _expr_has_name(arg, unsafe_sql_vars):
                return True

    return False


def _is_path_like_name(name: str) -> bool:
    lowered = name.lower()
    return any(hint in lowered for hint in PATH_HINTS)


def _expr_has_path_literal(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            value = child.value
            if "/" in value or "\\" in value or value.startswith("."):
                return True
    return False


def _detect_path_traversal_flow(code: str) -> bool:
    """
    Catch path traversal flow where a user-controlled filename is joined or
    concatenated into a path variable and later passed to open().
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    input_vars = set()
    path_vars = set()
    unsafe_path_vars = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not targets:
            continue

        value = node.value
        is_request_input = any(
            isinstance(child, ast.Attribute) and child.attr in {"args", "form", "files", "json", "data"}
            for child in ast.walk(value)
        ) or any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == "input"
            for child in ast.walk(value)
        )

        if is_request_input:
            input_vars.update(targets)

        has_path_name = any(_is_path_like_name(target) for target in targets)
        has_path_literal = _expr_has_path_literal(value)
        has_input_var = _expr_has_name(value, input_vars)
        has_path_var = _expr_has_name(value, path_vars)
        has_unsafe_path_var = _expr_has_name(value, unsafe_path_vars)
        has_concat = _expr_has_concat(value)

        if has_path_name or has_path_literal or has_path_var:
            path_vars.update(targets)

        if (
            (has_concat and (has_input_var or has_unsafe_path_var))
            or (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Attribute)
                and value.func.attr == "join"
                and (has_input_var or has_unsafe_path_var)
            )
        ):
            unsafe_path_vars.update(targets)

    if not unsafe_path_vars:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name not in PATH_SINKS:
            continue

        for arg in node.args:
            if isinstance(arg, ast.Name) and arg.id in unsafe_path_vars:
                return True
            if _expr_has_name(arg, unsafe_path_vars):
                return True

    return False


def _identify_vulnerability_type(code: str) -> Dict:
    features = extract_features(code)
    feature_map = dict(zip(FEATURE_NAMES, features))
    fired = [name for name, value in feature_map.items() if value > 0]
    sql_flow_detected = _detect_sql_injection_flow(code)
    path_flow_detected = _detect_path_traversal_flow(code)
    if sql_flow_detected:
        fired.append("phase3_sql_query_flow")
    if path_flow_detected:
        fired.append("phase3_path_traversal_flow")

    if feature_map.get("f2_hardcoded_secret", 0) > 0:
        vuln_type = "hardcoded_secret"
    elif feature_map.get("f1_sql_concat", 0) > 0 or sql_flow_detected:
        vuln_type = "sql_injection"
    elif feature_map.get("f5_cmd_injection", 0) > 0:
        vuln_type = "cmd_injection"
    elif feature_map.get("f3_eval_exec", 0) > 0:
        vuln_type = "insecure_eval"
    elif feature_map.get("f4_path_traversal", 0) > 0 or path_flow_detected:
        vuln_type = "path_traversal"
    else:
        vuln_type = "unknown"

    return {
        "vulnerability_type": vuln_type,
        "features_fired": fired,
        "has_security_signal": vuln_type != "unknown",
    }


def _retrieve_owasp_context(vulnerability_type: str, top_k: int = 3) -> List[Dict]:
    metadata = _resources["metadata"]

    query = TYPE_QUERIES.get(vulnerability_type, TYPE_QUERIES["unknown"])
    query_terms = {
        term.lower()
        for term in query.replace("/", " ").replace("-", " ").split()
        if len(term) >= 4
    }

    scored = []
    for item in metadata:
        text = str(item.get("text", ""))
        source = str(item.get("source", "unknown"))
        haystack = f"{source}\n{text}".lower()
        score = sum(1 for term in query_terms if term in haystack)
        if vulnerability_type in source.lower():
            score += 3
        if score > 0:
            scored.append((score, item))

    if not scored:
        scored = [(1, item) for item in metadata[:top_k]]

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [
        {
            "score": float(score),
            "source": item.get("source", "unknown"),
            "text": item.get("text", ""),
        }
        for score, item in scored[:top_k]
    ]


def _parse_groq_response(text: str, default_ref: str) -> Dict:
    sections = {"DANGER": "", "FIX": "", "REF": ""}
    current = None

    for line in text.splitlines():
        stripped = line.strip()
        upper = stripped.upper()
        if upper.startswith("DANGER:"):
            current = "DANGER"
            sections[current] = stripped.split(":", 1)[1].strip()
        elif upper.startswith("FIX:"):
            current = "FIX"
            sections[current] = stripped.split(":", 1)[1].strip()
        elif upper.startswith("REF:"):
            current = "REF"
            sections[current] = stripped.split(":", 1)[1].strip()
        elif current:
            if sections[current]:
                sections[current] += "\n"
            sections[current] += line.rstrip() if current == "FIX" else stripped

    return {
        "danger": sections["DANGER"].strip(),
        "fix": sections["FIX"].strip(),
        "owasp_ref": sections["REF"].strip() or default_ref,
    }


def _generate_explanation(
    code: str,
    vulnerability_type: str,
    context_docs: List[Dict],
) -> Dict:
    context = "\n\n".join(
        f"Source: {doc['source']}\n{doc['text']}" for doc in context_docs
    )
    default_ref = context_docs[0]["source"] if context_docs else "OWASP"

    prompt = f"""
You are SecureScope AI, a Python security assistant.

VULNERABILITY TYPE:
{vulnerability_type}

PYTHON CODE:
{code}

OWASP CONTEXT:
{context}

Return exactly this format:

DANGER:
One concise sentence explaining the security impact.

FIX:
Only the corrected Python code.
No explanation.
No markdown.
No triple backticks.

REF:
Most relevant OWASP document name.
""".strip()

    start = time.perf_counter()
    try:
        response = _resources["groq"].chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Return only DANGER, FIX, and REF sections.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=450,
        )
        LOGGER.info(
            "Groq explanation latency %.2f ms",
            (time.perf_counter() - start) * 1000,
        )
        content = response.choices[0].message.content or ""
        return _parse_groq_response(content, default_ref)
    except Exception as exc:
        raise RuntimeError(f"Groq API failed: {exc}") from exc


def scan_deep_phase3(code: str) -> Dict:
    if not phase3_available():
        load_phase3_resources()

    if not phase3_available():
        raise RuntimeError(_load_error or "Phase 3 models are unavailable.")

    start_total = time.perf_counter()

    start = time.perf_counter()
    binary = _predict_codebert_binary(code)
    LOGGER.info(
        "Phase 3 CodeBERT inference %.2f ms",
        (time.perf_counter() - start) * 1000,
    )

    start = time.perf_counter()
    type_result = _identify_vulnerability_type(code)
    LOGGER.info(
        "Phase 3 type identification %.2f ms",
        (time.perf_counter() - start) * 1000,
    )

    feature_detected = bool(type_result["has_security_signal"])
    is_vulnerable = bool(binary["is_vulnerable"] or feature_detected)
    decision_confidence = binary["confidence"]
    if feature_detected:
        decision_confidence = max(decision_confidence, 0.95)

    confidence = round(decision_confidence, 4)
    if not is_vulnerable:
        return {
            "is_vulnerable": False,
            "confidence": confidence,
            "risk_level": "SAFE",
            "vulnerability_type": "unknown",
            "danger": "",
            "fix": "",
            "owasp_ref": "",
            "pipeline": "phase3_rag_v1",
            "llm": GROQ_MODEL,
            "scan_time_ms": round((time.perf_counter() - start_total) * 1000, 2),
        }

    vulnerability_type = type_result["vulnerability_type"]
    if vulnerability_type == "unknown":
        return {
            "is_vulnerable": True,
            "confidence": confidence,
            "risk_level": _risk_level(decision_confidence, True),
            "vulnerability_type": "unknown",
            "danger": "",
            "fix": "",
            "owasp_ref": "",
            "pipeline": "phase3_rag_v1",
            "llm": GROQ_MODEL,
            "scan_time_ms": round((time.perf_counter() - start_total) * 1000, 2),
        }

    start = time.perf_counter()
    context_docs = _retrieve_owasp_context(vulnerability_type, top_k=3)
    LOGGER.info(
        "Phase 3 OWASP retrieval %.2f ms",
        (time.perf_counter() - start) * 1000,
    )

    explanation = _generate_explanation(code, vulnerability_type, context_docs)

    return {
        "is_vulnerable": True,
        "confidence": confidence,
        "risk_level": _risk_level(decision_confidence, True),
        "vulnerability_type": vulnerability_type,
        "danger": explanation["danger"],
        "fix": explanation["fix"],
        "owasp_ref": explanation["owasp_ref"],
        "pipeline": "phase3_rag_v1",
        "llm": GROQ_MODEL,
        "scan_time_ms": round((time.perf_counter() - start_total) * 1000, 2),
    }
