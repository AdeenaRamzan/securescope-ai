import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.core.feature_extractor import FEATURE_NAMES, extract_features
from src.core.phase3_pipeline import _identify_vulnerability_type


def test_phase3_identifies_mixed_sql_and_command_injection():
    code = """import sqlite3
import subprocess


def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    return cursor.fetchone()


def ping(host):
    command = f"ping -c 1 {host}"
    return subprocess.check_output(command, shell=True)
"""

    result = _identify_vulnerability_type(code)

    assert result["vulnerability_type"] == "multiple"
    assert result["detected_types"] == ["sql_injection", "cmd_injection"]
    assert "phase3_sql_query_flow" in result["features_fired"]
    assert "phase3_cmd_injection_flow" in result["features_fired"]


def test_phase3_identifies_inline_flask_open_redirect():
    code = """from flask import redirect, request

@app.route('/go')
def go():
    return redirect(request.args.get('next'))
"""

    result = _identify_vulnerability_type(code)

    assert result["vulnerability_type"] == "open_redirect"
    assert result["detected_types"] == ["open_redirect"]
    assert "phase3_open_redirect_flow" in result["features_fired"]


def test_phase3_identifies_pathlib_read_text_path_traversal():
    code = """from pathlib import Path

def read_file(name):
    path = Path("uploads") / name
    return path.read_text()
"""

    result = _identify_vulnerability_type(code)

    assert result["vulnerability_type"] == "path_traversal"
    assert result["detected_types"] == ["path_traversal"]
    assert "phase3_path_traversal_flow" in result["features_fired"]


def test_feature_extractor_flags_pathlib_read_text_path_traversal():
    code = """from pathlib import Path

def read_file(name):
    path = Path("uploads") / name
    return path.read_text()
"""

    feature_map = dict(zip(FEATURE_NAMES, extract_features(code)))

    assert feature_map["f4_path_traversal"] == 1.0


def test_phase3_identifies_direct_os_system_command_injection():
    code = """import os

def run_command(user_input):
    os.system(user_input)
"""

    result = _identify_vulnerability_type(code)

    assert result["vulnerability_type"] == "cmd_injection"
    assert result["detected_types"] == ["cmd_injection"]
    assert "phase3_cmd_injection_flow" in result["features_fired"]


def test_feature_extractor_flags_direct_os_system_command_injection():
    code = """import os

def run_command(user_input):
    os.system(user_input)
"""

    feature_map = dict(zip(FEATURE_NAMES, extract_features(code)))

    assert feature_map["f5_cmd_injection"] == 1.0
