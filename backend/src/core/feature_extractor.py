# %%
# ── BLOCK 1 ──────────────────────────────────────
# Title: Verify Setup
# Purpose: Confirm Python version and libraries work

import sys
print(f"Python version: {sys.version}")

import pandas as pd
import numpy as np
import tensorflow as tf
import sklearn

print(f"Pandas: {pd.__version__}")
print(f"NumPy: {np.__version__}")
print(f"TensorFlow: {tf.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print("\nAll libraries loaded. Setup is correct.")
# %%
# ── BLOCK 1 ──────────────────────────────────────
# Title: Imports
# Purpose: Load libraries needed for feature extraction

import ast
import re

print("Imports loaded.")


# %%
# ── BLOCK 2 ──────────────────────────────────────
# Title: Feature Extractor — Regex + AST combined
# Purpose: Extract 12 features from Python code
# Features 1-10: Regex based (fast, pattern matching)
# Features 11-12: AST based (structural, more accurate)

import ast
import re

def extract_features(code: str) -> list:

    # Parse code into AST tree
    # If code has syntax errors return all zeros
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [0] * 12

    # ── REGEX FEATURES ────────────────────────────

    # F1: SQL injection — string concat near SQL keyword
    f1 = int(bool(
        re.search(r'["\'].*SELECT.*["\'].*\+', code, re.IGNORECASE) or
        re.search(r'\+.*["\'].*SELECT', code, re.IGNORECASE) or
        re.search(r'["\'].*WHERE.*["\'].*\+', code, re.IGNORECASE)
    ))

    # F2: Hardcoded secret — sensitive name assigned a string
    sensitive = ['password', 'secret', 'api_key', 'token', 'pwd', 'key']
    f2 = int(any(
        re.search(rf'{name}\s*=\s*["\']', code, re.IGNORECASE)
        for name in sensitive
    ))

    # F3: Insecure eval or exec call
    f3 = int(bool(
        re.search(r'\beval\s*\(', code) or
        re.search(r'\bexec\s*\(', code)
    ))

    # F4: Path traversal — open() with concat OR path variable built from concat
    # Pattern A: open('/uploads/' + filename)     — direct concat in open()
    # Pattern B: path = '/templates/' + name      — concat on separate line
    f4 = int(bool(
        re.search(r'open\s*\([^)]*\+', code) or
        re.search(r'=\s*[\'"][/\\][^\'"]*[\'"]\s*\+', code)
    ))

    # F5: Command injection — os.system concat or shell=True
    f5 = int(bool(
        re.search(r'os\.system\s*\(.*\+', code) or
        re.search(r'subprocess.*shell\s*=\s*True', code)
    ))

    # F6: AST node count — more reliable than line count
    f6 = sum(1 for _ in ast.walk(tree))

    # F7: Number of string literals (will be scaled later)
    f7 = len(re.findall(r'["\'][^"\']*["\']', code))

    # F8: Uses os.environ — SAFE signal
    f8 = int('os.environ' in code)

    # F9: Uses parameterized query — SAFE signal
    f9 = int(bool(
        re.search(r'execute\s*\(.*[?%]', code) or
        re.search(r'execute\s*\(.*,\s*\(', code)
    ))

    # F10: Has user input reference
    f10 = int(bool(
        re.search(r'\b(input|request|user_input)\b', code)
    ))

    # ── AST FEATURES ──────────────────────────────

    # F11: Count dangerous function calls
    # AST catches eval(x) AND eval  ( x ) — both are Call nodes
    dangerous_sinks = {'eval', 'exec', 'system', 'popen', 'execute'}
    f11 = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name in dangerous_sinks:
                f11 += 1

    # F12: Hardcoded string assigned to sensitive variable
    # AST checks structure — catches password="x" not password=env_var
    sensitive_names = {'password', 'secret', 'api_key', 'token', 'pwd', 'key'}
    f12 = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id.lower() in sensitive_names:
                        if isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, str):
                                f12 += 1

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12]


print("Feature extractor defined.")
print(f"Returns {len(extract_features('x = 1'))} features per code sample.")

# %%
# ── BLOCK 3 ──────────────────────────────────────
# Title: Load and combine all 5 datasets
# Purpose: Load all JSON files, combine into one
#          DataFrame, verify counts and quality

import pandas as pd
import json
import os

# ── Locate data/custom folder ─────────────────────
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, '..', '..', 'data', 'custom')
data_dir = os.path.normpath(data_dir)

print(f"Loading from: {data_dir}")

# ── Load all 5 JSON files ─────────────────────────
files = [
    'sql_injection.json',
    'hardcoded_secrets.json',
    'insecure_eval.json',
    'path_traversal.json',
    'command_injection.json',
]

all_examples = []
for fname in files:
    fpath = os.path.join(data_dir, fname)
    with open(fpath, 'r') as f:
        examples = json.load(f)
        all_examples.extend(examples)
    print(f"  {fname}: {len(examples)} examples")

# ── Convert to DataFrame ──────────────────────────
df = pd.DataFrame(all_examples)

print(f"\n{'='*40}")
print(f"COMBINED DATASET SUMMARY")
print(f"{'='*40}")
print(f"Total rows:           {len(df)}")
print(f"Vulnerable (label=1): {(df['label']==1).sum()}")
print(f"Safe       (label=0): {(df['label']==0).sum()}")
print(f"Columns:              {list(df.columns)}")
print(f"\nType distribution:")
print(df['type'].value_counts().to_string())
print(f"\nSample code preview:")
print(df['code'].iloc[0][:120])


# %%
# ── BLOCK 4 ──────────────────────────────────────
# Title: Extract features from all examples
# Purpose: Run extract_features() on every code
#          sample, build feature matrix, verify
#          features are firing correctly

# ── Run feature extraction ────────────────────────
print("Extracting features from 250 examples...")

feature_rows = []
failed = 0

for i, row in df.iterrows():
    features = extract_features(row['code'])
    feature_rows.append(features)
    if sum(features) == 0:
        failed += 1

# ── Build feature DataFrame ───────────────────────
feature_names = [
    'f1_sql_concat',
    'f2_hardcoded_secret',
    'f3_eval_exec',
    'f4_path_traversal',
    'f5_cmd_injection',
    'f6_func_length',
    'f7_string_count',
    'f8_uses_environ',
    'f9_parameterized',
    'f10_user_input',
    'f11_ast_dangerous_calls',
    'f12_ast_hardcoded_assign'
]

X = pd.DataFrame(feature_rows, columns=feature_names)
y = df['label'].values

print(f"Feature matrix shape: {X.shape}")
print(f"Labels shape: {y.shape}")
print(f"All-zero rows: {failed} out of {len(df)}")

print(f"\nFeature firing rates (% of examples where feature > 0):")
for col in feature_names:
    rate = (X[col] > 0).mean() * 100
    print(f"  {col:<25}: {rate:.1f}%")

print(f"\nSample — first vulnerable example features:")
first_vuln = X[y == 1].iloc[0]
print(first_vuln.to_string())

print(f"\nSample — first safe example features:")
first_safe = X[y == 0].iloc[0]
print(first_safe.to_string())

# %%


# %%
# ── BLOCK 5 ──────────────────────────────────────
# Title: Save feature matrix to CSV
# Purpose: Save X (features) and y (labels) as one
#          CSV file to data/processed/features.csv

# ── Combine features and labels ───────────────────
df_features = X.copy()
df_features['label'] = y

# ── Save to processed folder ──────────────────────
processed_dir = os.path.normpath(
    os.path.join(base_dir, '..', '..', 'data', 'processed')
)
os.makedirs(processed_dir, exist_ok=True)

save_path = os.path.join(processed_dir, 'features.csv')
df_features.to_csv(save_path, index=False)

print(f"Saved: {save_path}")
print(f"Shape: {df_features.shape}")
print(f"\nFirst 3 rows:")
print(df_features.head(3).to_string())
print(f"\nLabel distribution:")
print(df_features['label'].value_counts().to_string())
# %%
