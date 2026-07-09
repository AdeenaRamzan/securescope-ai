# %%
# backend/src/core/feature_extractor.py
# Purpose: Convert raw Python code string into
#          22 numerical features for the ensemble

import ast
import re
from typing import List


SUBPROCESS_SINKS = {'call', 'run', 'Popen', 'check_output', 'system', 'popen'}


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _has_shell_true(node: ast.Call) -> bool:
    return any(
        keyword.arg == 'shell'
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in node.keywords
    )


def _argv_has_dynamic_arg(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, (ast.BinOp, ast.JoinedStr, ast.Call)):
        return True
    if not isinstance(node, (ast.List, ast.Tuple)):
        return False

    for element in node.elts:
        if isinstance(element, ast.Constant) and isinstance(element.value, str):
            continue
        return True

    return False


def _has_dynamic_subprocess_call(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_name = _call_name(node)
        if func_name not in SUBPROCESS_SINKS:
            continue

        if _has_shell_true(node):
            return True
        if any(_argv_has_dynamic_arg(arg) for arg in node.args):
            return True

    return False


def _function_param_names(tree: ast.AST) -> set[str]:
    params = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        params.update(arg.arg for arg in node.args.args)
        params.update(arg.arg for arg in node.args.posonlyargs)
        params.update(arg.arg for arg in node.args.kwonlyargs)
        if node.args.vararg:
            params.add(node.args.vararg.arg)
        if node.args.kwarg:
            params.add(node.args.kwarg.arg)
    return params


def _expr_has_name(node: ast.AST, names: set[str]) -> bool:
    return any(isinstance(child, ast.Name) and child.id in names for child in ast.walk(node))


def _expr_has_path_join_operator(node: ast.AST) -> bool:
    return any(isinstance(child, ast.BinOp) and isinstance(child.op, ast.Div) for child in ast.walk(node))


def _expr_has_path_literal(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            value = child.value
            if "/" in value or "\\" in value or value.startswith(".") or value in {"uploads", "upload", "files", "static"}:
                return True
    return False


def _has_dynamic_path_read(tree: ast.AST) -> bool:
    input_vars = _function_param_names(tree)
    path_vars = set()
    unsafe_path_vars = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not targets:
            continue

        value = node.value
        has_path_name = any(
            any(hint in target.lower() for hint in ("path", "file", "filename", "dir", "directory"))
            for target in targets
        )
        has_path_literal = _expr_has_path_literal(value)
        has_path_var = _expr_has_name(value, path_vars)
        has_unsafe_path_var = _expr_has_name(value, unsafe_path_vars)
        has_dynamic_input = _expr_has_name(value, input_vars) or has_unsafe_path_var
        has_dynamic_join = isinstance(value, ast.BinOp) or _expr_has_path_join_operator(value)

        if has_path_name or has_path_literal or has_path_var:
            path_vars.update(targets)
        if has_dynamic_join and has_dynamic_input and (has_path_name or has_path_literal or has_path_var):
            unsafe_path_vars.update(targets)

    if not unsafe_path_vars:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func_name = _call_name(node)
        if func_name == "open" and any(_expr_has_name(arg, unsafe_path_vars) for arg in node.args):
            return True
        if func_name in {"read_text", "read_bytes"} and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in unsafe_path_vars:
                return True

    return False


FEATURE_NAMES = [
    'f1_sql_concat',
    'f2_hardcoded_secret',
    'f3_eval_exec',
    'f4_path_traversal',
    'f5_cmd_injection',
    'f6_ast_nodes',
    'f7_string_count',
    'f8_uses_environ',
    'f9_parameterized',
    'f10_user_input',
    'f11_ast_dangerous_calls',
    'f12_ast_hardcoded_assign',
    'f13_user_controlled_input',
    'f14_db_operation',
    'f15_file_subprocess',
    'f16_dangerous_deserialize',
    'f17_nesting_depth',
    'f18_param_count',
    'f19_exception_handling',
    'f20_string_formatting',
    'f21_network_calls',
    'f22_weak_crypto'
]


def extract_features(code: str) -> List[float]:
    """
    Convert Python code string into 22 numerical features.
    Returns list of 22 numbers ready for model input.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [0.0] * 22

    # ── F1: SQL injection ─────────────────────────
    f1 = int(bool(
        re.search(r'["\'].*SELECT.*["\'].*\+', code, re.IGNORECASE) or
        re.search(r'\+.*["\'].*SELECT', code, re.IGNORECASE) or
        re.search(r'["\'].*WHERE.*["\'].*\+', code, re.IGNORECASE)
    ))

    # ── F2: Hardcoded secret (regex) ──────────────
    sensitive = ['password', 'secret', 'api_key', 'token', 'pwd', 'key']
    f2 = int(any(
        re.search(rf'{name}\s*=\s*["\']', code, re.IGNORECASE)
        for name in sensitive
    ))

    # ── F3: Insecure eval/exec ────────────────────
    f3 = int(bool(
        re.search(r'\beval\s*\(', code) or
        re.search(r'\bexec\s*\(', code)
    ))

    # ── F4: Path traversal ────────────────────────
    f4 = int(bool(
        re.search(r'open\s*\([^)]*\+', code) or
        re.search(r'=\s*[\'"][/\\][^\'"]*[\'"]\s*\+', code) or
        _has_dynamic_path_read(tree)
    ))

    # ── F5: Command injection ─────────────────────
    f5 = int(bool(
        re.search(r'os\.system\s*\(.*\+', code) or
        re.search(r'subprocess.*shell\s*=\s*True', code) or
        _has_dynamic_subprocess_call(tree)
    ))

    # ── F6: AST node count ────────────────────────
    f6 = sum(1 for _ in ast.walk(tree))

    # ── F7: String literal count ──────────────────
    f7 = len(re.findall(r'["\'][^"\']*["\']', code))

    # ── F8: Uses os.environ (safe signal) ─────────
    f8 = int('os.environ' in code)

    # ── F9: Parameterized query (safe signal) ─────
    f9 = int(bool(
    re.search(r'execute\s*\(["\'][^"\']*\?["\'],\s*[\(\[]', code) or
    re.search(r'execute\s*\(["\'][^"\']*%s["\'],\s*[\(\[]', code) or
    re.search(r'execute\s*\(["\'][^"\']*%[^"\']*["\'],\s*[\(\[]', code)
    ))

    # ── F10: User input reference ─────────────────
    f10 = int(bool(
        re.search(r'\b(input|request|user_input)\b', code)
    ))

    # ── F11: AST dangerous calls ──────────────────
    dangerous_sinks = {'eval', 'exec', 'system', 'popen', 'execute', *SUBPROCESS_SINKS}
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

    # ── F12: AST hardcoded secret ─────────────────
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

    # ── F13: User controlled input ────────────────
    f13 = int(bool(
        re.search(r'request\.(args|form|get|POST|data|json)', code) or
        re.search(r'request\[', code) or
        re.search(r'flask\.request', code) or
        re.search(r'self\.(request|req)\.', code)
    ))

    # ── F14: Database operation ───────────────────
    f14 = int(bool(
        re.search(r'\.(execute|query|filter|raw|cursor)\s*\(', code) or
        re.search(r'(SELECT|INSERT|UPDATE|DELETE)', code, re.IGNORECASE) or
        re.search(r'db\.(session|execute|query)', code) or
        re.search(r'cursor\.(execute|fetchall|fetchone)', code)
    ))

    # ── F15: File or subprocess ───────────────────
    f15 = int(bool(
        re.search(r'\bopen\s*\(', code) or
        re.search(r'os\.(system|popen|makedirs|remove|rename)', code) or
        re.search(r'subprocess\.(call|run|Popen|check_output)', code) or
        re.search(r'shutil\.(copy|move|rmtree)', code)
    ))

    # ── F16: Dangerous deserialization ───────────
    f16 = int(bool(
        re.search(r'pickle\.(loads|load|dumps)', code) or
        re.search(r'yaml\.load\s*\(', code) or
        re.search(r'marshal\.(loads|load)', code) or
        re.search(r'jsonpickle\.decode', code) or
        re.search(r'shelve\.open', code)
    ))

    # ── F17: Maximum nesting depth ────────────────
    lines = code.split('\n')
    max_indent = 0
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
    f17 = max_indent // 4

    # ── F18: Function parameter count ────────────
    f18 = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            f18 = max(f18, len(node.args.args))

    # ── F19: Exception handling ───────────────────
    f19 = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                f19 = 2
            else:
                f19 = max(f19, 1)

    # ── F20: String formatting ────────────────────
    f20 = int(bool(
        re.search(r'\.format\s*\(', code) or
        re.search(r'f["\'].*{.*}.*["\']', code) or
        re.search(r'%\s*["\(]', code)
    ))

    # ── F21: Network calls ────────────────────────
    f21 = int(bool(
        re.search(r'requests\.(get|post|put|delete|patch)', code) or
        re.search(r'urllib\.(request|urlopen)', code) or
        re.search(r'\bsocket\b', code) or
        re.search(r'http\.client', code)
    ))

    # ── F22: Weak crypto ──────────────────────────
    f22 = int(bool(
        re.search(r'\brandom\.(random|randint|choice)\b', code) or
        re.search(r'hashlib\.(md5|sha1)\b', code) or
        re.search(r'MD5|SHA1', code) or
        re.search(r'DES|RC4|ECB', code)
    ))

    return [
        float(f1), float(f2), float(f3), float(f4),
        float(f5), float(f6), float(f7), float(f8),
        float(f9), float(f10), float(f11), float(f12),
        float(f13), float(f14), float(f15), float(f16),
        float(f17), float(f18), float(f19), float(f20),
        float(f21), float(f22)
    ]
