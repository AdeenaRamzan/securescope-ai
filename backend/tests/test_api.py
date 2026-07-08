import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

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
