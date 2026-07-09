import type {
  ScanMode,
  Phase1Result,
  Phase2Result,
  CascadeResult,
  Phase3Result,
  ScanResult,
} from "./types";
import { SCAN_MODE_META } from "./types";

const API_BASE = "https://adeenaramzan93-securescope-ai-api.hf.space";

async function post<T>(endpoint: string, code: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language: "python" }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `Server responded with ${res.status}${text ? `: ${text}` : ""}`
    );
  }

  return res.json() as Promise<T>;
}

export async function scanCode(
  code: string,
  mode: ScanMode
): Promise<ScanResult> {
  const { endpoint } = SCAN_MODE_META[mode];

  switch (mode) {
    case "quick": {
      const data = await post<Phase1Result>(endpoint, code);
      return { ...data, _mode: "quick" };
    }
    case "bilstm": {
      const data = await post<Phase2Result>(endpoint, code);
      return { ...data, _mode: "bilstm" };
    }
    case "cascade": {
      const data = await post<CascadeResult>(endpoint, code);
      return { ...data, _mode: "cascade" };
    }
    case "explain": {
      // Run ensemble (Phase 1) and deep scan in parallel.
      // If the ensemble detects a vulnerability but the deep scan's
      // CodeBERT binary classifier misses it, override with ensemble result
      // and generate fallback explanations from detected features.
      const [deepData, quickData] = await Promise.all([
        post<Phase3Result>(endpoint, code),
        post<Phase1Result>("/scan", code).catch(() => null),
      ]);

      const ensembleVulnerable = quickData?.is_vulnerable === true;
      const deepMissed = !deepData.is_vulnerable && ensembleVulnerable;
      const deepHasExplanation = deepData.danger && deepData.danger.trim().length > 0;

      if (deepMissed && !deepHasExplanation && quickData) {
        const fallback = buildFallbackExplanation(quickData.features_fired);
        return {
          ...deepData,
          _mode: "explain" as const,
          is_vulnerable: true,
          risk_level: quickData.risk_level,
          confidence: quickData.confidence,
          vulnerability_type: fallback.vulnType,
          danger: fallback.danger,
          fix: fallback.fix,
          owasp_ref: fallback.owaspRef,
          pipeline: "ensemble_override",
        };
      }

      return {
        ...deepData,
        _mode: "explain" as const,
        ...(deepMissed
          ? {
              is_vulnerable: true,
              risk_level: quickData!.risk_level,
              confidence: quickData!.confidence,
            }
          : {}),
      };
    }
  }
}

// ── Fallback explanations when ensemble detects what CodeBERT missed ──

interface FallbackExplanation {
  vulnType: string;
  danger: string;
  fix: string;
  owaspRef: string;
}

const FEATURE_EXPLANATIONS: Record<string, FallbackExplanation> = {
  uses_os_system: {
    vulnType: "cmd_injection",
    danger:
      "This code uses os.system() with user-controlled input, allowing an attacker to execute arbitrary operating system commands. An attacker could chain commands using shell metacharacters (;, &&, |, etc.) to run malicious commands, exfiltrate data, install backdoors, or completely compromise the server.",
    fix:
      "import subprocess\n\ndef run_command(user_input):\n    # Use subprocess with a fixed command and no shell=True\n    allowed_commands = {'ls', 'date', 'whoami'}\n    if user_input in allowed_commands:\n        result = subprocess.run(\n            [user_input],\n            capture_output=True, text=True,\n            shell=False\n        )\n        return result.stdout\n    else:\n        raise ValueError('Command not allowed')",
    owaspRef: "OS Command Injection Defense Cheat Sheet",
  },
  uses_subprocess_shell: {
    vulnType: "cmd_injection",
    danger:
      "This code uses subprocess with shell=True and user-controlled input, allowing command injection. An attacker can inject shell metacharacters to execute arbitrary commands on the system.",
    fix:
      "import subprocess\n\ndef run_command(cmd_args):\n    # Never use shell=True with user input\n    result = subprocess.run(\n        cmd_args,  # pass as list, not string\n        capture_output=True, text=True,\n        shell=False\n    )\n    return result.stdout",
    owaspRef: "OS Command Injection Defense Cheat Sheet",
  },
  uses_eval: {
    vulnType: "insecure_eval",
    danger:
      "This code uses eval() or exec() with potentially untrusted input. An attacker can inject arbitrary Python code that will be executed with the application's privileges, leading to complete system compromise, data theft, or denial of service.",
    fix:
      "import ast\n\ndef safe_evaluate(expression):\n    # Use ast.literal_eval for safe evaluation of literals\n    try:\n        return ast.literal_eval(expression)\n    except (ValueError, SyntaxError):\n        raise ValueError('Invalid expression')",
    owaspRef: "Injection Prevention Cheat Sheet",
  },
  uses_exec: {
    vulnType: "insecure_eval",
    danger:
      "This code uses exec() which executes arbitrary Python code. If any part of the executed string is user-controlled, an attacker can run any Python code with full application privileges.",
    fix:
      "# Avoid exec() entirely. Use specific functions or a safe DSL instead.\n# If dynamic behavior is needed, use a whitelist approach:\n\nALLOWED_ACTIONS = {\n    'greet': lambda name: f'Hello, {name}!',\n    'add': lambda a, b: a + b,\n}\n\ndef run_action(action_name, *args):\n    if action_name not in ALLOWED_ACTIONS:\n        raise ValueError('Action not allowed')\n    return ALLOWED_ACTIONS[action_name](*args)",
    owaspRef: "Injection Prevention Cheat Sheet",
  },
  sql_concat: {
    vulnType: "sql_injection",
    danger:
      "This code constructs SQL queries using string concatenation with user input. An attacker can inject malicious SQL to bypass authentication, extract sensitive data, modify or delete records, or execute administrative database operations.",
    fix:
      "import sqlite3\n\ndef get_user(username):\n    conn = sqlite3.connect('db.sqlite')\n    # Use parameterized queries — NEVER concatenate user input\n    cursor = conn.execute(\n        'SELECT * FROM users WHERE name = ?',\n        (username,)\n    )\n    return cursor.fetchall()",
    owaspRef: "SQL Injection Prevention Cheat Sheet",
  },
  sql_format: {
    vulnType: "sql_injection",
    danger:
      "This code uses string formatting (f-strings, .format(), or %) to build SQL queries with user input. This is equivalent to string concatenation and is equally vulnerable to SQL injection attacks.",
    fix:
      "import sqlite3\n\ndef get_user(username):\n    conn = sqlite3.connect('db.sqlite')\n    # Use parameterized queries with ? placeholders\n    cursor = conn.execute(\n        'SELECT * FROM users WHERE name = ?',\n        (username,)\n    )\n    return cursor.fetchall()",
    owaspRef: "SQL Injection Prevention Cheat Sheet",
  },
  hardcoded_secret: {
    vulnType: "hardcoded_secret",
    danger:
      "This code contains hardcoded credentials, API keys, or secrets. If the source code is leaked, committed to version control, or accessed by unauthorized users, these secrets can be used to compromise connected services, databases, or APIs.",
    fix:
      "import os\nfrom dotenv import load_dotenv\n\nload_dotenv()\n\n# Load secrets from environment variables\nAPI_KEY = os.environ['API_KEY']\nDB_PASSWORD = os.environ['DB_PASSWORD']\n\n# Never hardcode secrets in source code",
    owaspRef: "Secrets Management Cheat Sheet",
  },
  path_traversal: {
    vulnType: "path_traversal",
    danger:
      "This code uses user-controlled input in file paths without proper sanitization. An attacker can use directory traversal sequences (../) to access files outside the intended directory, potentially reading sensitive system files like /etc/passwd or application configuration files.",
    fix:
      "import os\nfrom pathlib import Path\n\nBASE_DIR = Path('/app/uploads')\n\ndef read_file(filename):\n    # Resolve and validate the path stays within BASE_DIR\n    safe_path = (BASE_DIR / filename).resolve()\n    if not safe_path.is_relative_to(BASE_DIR):\n        raise ValueError('Access denied: path traversal detected')\n    return safe_path.read_text()",
    owaspRef: "Input Validation Cheat Sheet",
  },
};

function buildFallbackExplanation(featuresFired: string[]): FallbackExplanation {
  // Try to match a detected feature to a known explanation
  for (const feature of featuresFired) {
    const key = feature.toLowerCase();
    if (FEATURE_EXPLANATIONS[key]) {
      return FEATURE_EXPLANATIONS[key];
    }
  }

  // Generic fallback if no specific feature matches
  return {
    vulnType: "unknown",
    danger:
      `The ensemble ML models (ANN, XGBoost, LightGBM) detected a potential security vulnerability in this code with high confidence. Features triggered: ${featuresFired.join(", ") || "N/A"}. Manual review is strongly recommended.`,
    fix:
      "# Review the flagged code carefully.\n# Common fixes include:\n# - Using parameterized queries instead of string concatenation\n# - Avoiding eval/exec with user input\n# - Using subprocess without shell=True\n# - Loading secrets from environment variables\n# - Validating and sanitizing all user inputs",
    owaspRef: "Secure Coding Practices Quick Reference Guide",
  };
}
