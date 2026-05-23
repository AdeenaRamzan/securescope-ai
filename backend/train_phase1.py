"""
Phase 1 ensemble retraining: synthetic JSON + PyCode Vul train,
holdout PyCode Vul test, 22-feature extractor, ANN + XGBoost + LightGBM.

Usage (from backend/):
    ..\\backend\\venv\\Scripts\\python.exe train_phase1.py
    ..\\backend\\venv\\Scripts\\python.exe train_phase1.py --skip-ann   # trees only (fast smoke)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras

# Allow imports from backend/
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from src.core.feature_extractor import FEATURE_NAMES, extract_features  # noqa: E402

CUSTOM_FILES = [
    "sql_injection.json",
    "hardcoded_secrets.json",
    "insecure_eval.json",
    "path_traversal.json",
    "command_injection.json",
]
RAW_TRAIN = "PyCode_Vul_train.xlsx"
RAW_TEST = "PyCode_Vul_test.csv"
MODEL_VERSION = "v3_ensemble_phase1_r2"
RECALL_TARGET = 0.75


STATIC_SQL_EXAMPLES = [
    {
        "code": 'def list_products():\n    cursor.execute("SELECT * FROM products")\n    return cursor.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def list_users():\n    cursor.execute("SELECT id, name FROM users")\n    return cursor.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def list_orders():\n    db.execute("SELECT * FROM orders")\n    return db.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def count_products():\n    cursor.execute("SELECT COUNT(*) FROM products")\n    return cursor.fetchone()[0]',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def get_active_products():\n    return conn.execute("SELECT * FROM products WHERE active = 1").fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def list_categories():\n    cursor.execute("SELECT * FROM categories ORDER BY name")\n    return cursor.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def fetch_all_posts():\n    db.execute("SELECT * FROM posts")\n    return db.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def list_inventory():\n    cursor.execute("SELECT sku, quantity FROM inventory")\n    return cursor.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def get_default_settings():\n    return db.execute("SELECT * FROM settings WHERE is_default = 1").fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def list_employees():\n    conn.execute("SELECT id, name, department FROM employees")\n    return conn.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def purge_expired_sessions():\n    cursor.execute("DELETE FROM sessions WHERE expires_at < NOW()")\n    return cursor.rowcount',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def seed_admin_role():\n    db.execute("INSERT INTO roles (name) VALUES (\'admin\')")\n    return db.commit()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'class ProductRepository:\n    def list_all(self):\n        self.db.execute("SELECT * FROM products")\n        return self.db.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def refresh_materialized_view():\n    cursor.execute("REFRESH MATERIALIZED VIEW sales_summary")\n    return None',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def list_audit_logs():\n    query = "SELECT * FROM audit_logs ORDER BY created_at DESC"\n    cursor.execute(query)\n    return cursor.fetchall()',
        "label": 0,
        "type": "safe_static_sql",
    },
    {
        "code": 'def get_schema_version():\n    return cursor.execute("SELECT version FROM schema_migrations").fetchone()',
        "label": 0,
        "type": "safe_static_sql",
    },
]


def merge_static_sql_examples(custom_dir: Path) -> int:
    """Append static safe SQL examples to sql_injection.json (dedupe by code)."""
    path = custom_dir / "sql_injection.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    existing_codes = {row["code"] for row in data}
    added = 0
    for ex in STATIC_SQL_EXAMPLES:
        if ex["code"] not in existing_codes:
            data.append(ex)
            existing_codes.add(ex["code"])
            added += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"sql_injection.json: {len(data)} total (+{added} static safe examples)")
    return added


def load_synthetic(custom_dir: Path) -> pd.DataFrame:
    rows = []
    for fname in CUSTOM_FILES:
        path = custom_dir / fname
        with open(path, encoding="utf-8") as f:
            examples = json.load(f)
        rows.extend(examples)
        print(f"  {fname}: {len(examples)}")
    df = pd.DataFrame(rows)
    return df[["code", "label"]]


def load_pycode_train(raw_dir: Path) -> pd.DataFrame:
    path = raw_dir / RAW_TRAIN
    df = pd.read_excel(path)
    df = df[["vulnerable_function_source", "label"]]
    df.columns = ["code", "label"]
    df["code"] = df["code"].astype(str)
    df["label"] = df["label"].astype(int)
    return df


def load_pycode_test(raw_dir: Path) -> pd.DataFrame:
    path = raw_dir / RAW_TEST
    df = pd.read_csv(path)
    df = df.rename(columns={"function_code": "code", "class": "label"})
    df = df[["code", "label"]]
    df["code"] = df["code"].astype(str)
    df["label"] = df["label"].astype(int)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.dropna(subset=["code"]).copy()
    out["code"] = out["code"].astype(str)
    out = out[out["code"].str.strip().str.len() > 10]
    out = out.drop_duplicates(subset="code")
    out["label"] = out["label"].astype(int)
    return out.reset_index(drop=True)


def build_feature_matrix(codes: pd.Series, name: str) -> pd.DataFrame:
    rows = []
    errors = 0
    n = len(codes)
    start = time.time()
    for i, code in enumerate(codes):
        try:
            feats = extract_features(str(code))
        except Exception:
            errors += 1
            feats = [0.0] * 22
        rows.append(feats)
        if (i + 1) % 3000 == 0:
            print(f"  {name}: {i + 1}/{n} ({time.time() - start:.1f}s)")

    print(f"  {name}: done in {time.time() - start:.1f}s | errors={errors}")
    return pd.DataFrame(rows, columns=FEATURE_NAMES)


def extract_labeled(df: pd.DataFrame, name: str) -> pd.DataFrame:
    X = build_feature_matrix(df["code"], name)
    X["label"] = df["label"].values
    return X


def build_ann(input_dim: int) -> keras.Model:
    model = keras.Sequential([
        keras.layers.Input(shape=(input_dim,)),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0005),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.AUC(name="auc"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def find_best_threshold(y_true: np.ndarray, proba: np.ndarray) -> tuple[float, dict]:
    best_threshold = 0.5
    best_row = None
    for threshold in np.arange(0.20, 0.61, 0.01):
        y_pred = (proba >= threshold).astype(int)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        row = {
            "threshold": float(threshold),
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": rec,
            "f1": f1,
            "eligible": rec > RECALL_TARGET,
        }
        if best_row is None:
            best_row = row
            best_threshold = threshold
            continue
        if row["eligible"] and (not best_row["eligible"] or row["f1"] > best_row["f1"]):
            best_row = row
            best_threshold = threshold
        elif not best_row["eligible"] and row["f1"] > best_row["f1"]:
            best_row = row
            best_threshold = threshold
    return best_threshold, best_row  # type: ignore[return-value]


def metrics_dict(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 3),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrain Phase 1 ensemble")
    parser.add_argument(
        "--no-regenerate-seeds",
        action="store_true",
        help="Skip running sql_injection_seeds.py",
    )
    parser.add_argument(
        "--skip-ann",
        action="store_true",
        help="Reuse existing ann_v3_tuned.keras (trees + threshold only)",
    )
    args = parser.parse_args()

    custom_dir = BACKEND_DIR / "data" / "custom"
    raw_dir = BACKEND_DIR / "data" / "raw"
    models_dir = BACKEND_DIR / "models" / "saved"
    models_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_regenerate_seeds:
        merge_static_sql_examples(custom_dir)

    print("\n=== Load data ===")
    synthetic = load_synthetic(custom_dir)
    pycode_train = load_pycode_train(raw_dir)
    pycode_test = load_pycode_test(raw_dir)

    combined = pd.concat([synthetic, pycode_train], ignore_index=True)
    combined = clean_data(combined)
    print(f"Synthetic rows: {len(synthetic)}")
    print(f"Combined after clean: {len(combined)}")
    print(f"Labels: {combined['label'].value_counts().to_dict()}")

    print("\n=== Extract features (train) ===")
    train_df = extract_labeled(combined, "train")
    print("\n=== Extract features (holdout) ===")
    test_df = extract_labeled(pycode_test, "holdout")

    X = train_df[FEATURE_NAMES].values
    y = train_df["label"].values.astype(int)
    X_hold = test_df[FEATURE_NAMES].values
    y_hold = test_df["label"].values.astype(int)

    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr)
    X_val_scaled = scaler.transform(X_val)
    X_hold_scaled = scaler.transform(X_hold)

    scale_pos = (y_tr == 0).sum() / max((y_tr == 1).sum(), 1)
    print(f"\nscale_pos_weight: {scale_pos:.2f}")

    if args.skip_ann:
        ann_path = models_dir / "ann_v3_tuned.keras"
        print(f"Loading existing ANN: {ann_path}")
        ann_model = keras.models.load_model(ann_path)
    else:
        print("\n=== Train ANN ===")
        ann_model = build_ann(X_tr.shape[1])
        ann_model.fit(
            X_tr_scaled,
            y_tr,
            validation_data=(X_val_scaled, y_val),
            epochs=80,
            batch_size=32,
            class_weight={0: 1.0, 1: float(scale_pos)},
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor="val_auc", patience=12, mode="max", restore_best_weights=True
                ),
            ],
            verbose=1,
        )

    print("\n=== Train XGBoost ===")
    xgb_model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )
    xgb_model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)

    print("\n=== Train LightGBM ===")
    lgb_model = lgb.LGBMClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        class_weight={0: 1.0, 1: float(scale_pos)},
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )
    lgb_model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)])

    ann_proba = ann_model.predict(X_val_scaled, verbose=0).flatten()
    xgb_proba = xgb_model.predict_proba(X_val)[:, 1]
    lgb_proba = lgb_model.predict_proba(X_val)[:, 1]
    ensemble_val = (ann_proba + xgb_proba + lgb_proba) / 3

    best_threshold, best_val_row = find_best_threshold(y_val, ensemble_val)
    print(f"\nValidation best threshold: {best_threshold:.2f}")
    print(f"  Val metrics: {best_val_row}")

    ann_hold = ann_model.predict(X_hold_scaled, verbose=0).flatten()
    xgb_hold = xgb_model.predict_proba(X_hold)[:, 1]
    lgb_hold = lgb_model.predict_proba(X_hold)[:, 1]
    ensemble_hold = (ann_hold + xgb_hold + lgb_hold) / 3
    y_hold_pred = (ensemble_hold >= best_threshold).astype(int)
    holdout_metrics = metrics_dict(y_hold, y_hold_pred)

    print("\n=== Holdout (PyCode Vul test) ===")
    print(classification_report(y_hold, y_hold_pred, target_names=["Safe", "Vulnerable"]))
    print(holdout_metrics)

    print("\n=== Sanity: static safe SQL ===")
    sanity_cases = {
        "list_products_static": (
            'def list_products():\n'
            '    cursor.execute("SELECT * FROM products")\n'
            '    return cursor.fetchall()'
        ),
        "find_product_param": (
            'def find_product(name):\n'
            '    cursor.execute("SELECT * FROM products WHERE name = ?", (name,))\n'
            '    return cursor.fetchall()'
        ),
        "vuln_concat": (
            'def find_product(name):\n'
            '    sql = "SELECT * FROM products WHERE name = \'" + name + "\'"\n'
            '    return cursor.execute(sql)'
        ),
    }
    for name, code in sanity_cases.items():
        feats = np.array(extract_features(code)).reshape(1, -1)
        prob = (
            float(ann_model.predict(scaler.transform(feats), verbose=0)[0][0])
            + float(xgb_model.predict_proba(feats)[0][1])
            + float(lgb_model.predict_proba(feats)[0][1])
        ) / 3
        print(
            f"  {name}: prob={prob:.4f} "
            f"vuln={prob >= best_threshold} (t={best_threshold:.2f})"
        )

    print("\n=== Save models ===")
    ann_model.save(models_dir / "ann_v3_tuned.keras")
    joblib.dump(xgb_model, models_dir / "xgb_v3.pkl")
    joblib.dump(lgb_model, models_dir / "lgb_v3.pkl")
    joblib.dump(scaler, models_dir / "scaler_v3.pkl")

    config = {
        "version": MODEL_VERSION,
        "description": "Phase 1 ensemble — retrained with static safe SQL synthetic examples",
        "deployment": {
            "threshold": round(best_threshold, 2),
            "voting": "soft_average",
            "ann_uses_scaled_features": True,
            "tree_models_use_raw_features": True,
        },
        "models": {
            "ann": "ann_v3_tuned.keras",
            "xgboost": "xgb_v3.pkl",
            "lightgbm": "lgb_v3.pkl",
            "scaler": "scaler_v3.pkl",
        },
        "features": {"count": 22, "names": list(FEATURE_NAMES)},
        "training_data": {
            "synthetic": {
                "rows": int(len(synthetic)),
                "description": "Hand-crafted OWASP-aligned + static safe SQL examples",
            },
            "real": {
                "rows": int(len(pycode_train)),
                "source": "PyCode Vul train",
                "citation": "Karim et al. 2025, IEEE",
            },
            "combined_after_cleaning": int(len(combined)),
        },
        "evaluation": {
            "test_set": "PyCode Vul holdout",
            "test_rows": int(len(y_hold)),
            "safe_rows": int((y_hold == 0).sum()),
            "vulnerable_rows": int((y_hold == 1).sum()),
            "metrics": holdout_metrics,
        },
        "known_limitations": [
            "Features are hand-crafted regex + AST patterns",
            "Static literal SQL may still resemble DB-heavy vulnerable code",
            "Phase 2 BiLSTM on token sequences designed to address this",
        ],
        "next_phase": "Phase 2 — BiLSTM on tokenized code sequences",
    }
    with open(models_dir / "ensemble_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\nDone. Models saved to {models_dir}")
    print(f"Version: {MODEL_VERSION} | threshold: {best_threshold:.2f}")


if __name__ == "__main__":
    main()
