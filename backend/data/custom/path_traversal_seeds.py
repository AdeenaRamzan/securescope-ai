# %%
import json
import os

# IMPROVEMENTS FROM v1:
# 1. Added Flask request context (3 vuln entries) — real web download endpoint
# 2. Added class method context (2 entries)
# 3. Safe: more realpath+startswith combinations — strongest defense
# 4. Safe: added pathlib.Path usage — modern Python standard
# 5. Kept your extractor fix note at top — the two-line pattern detection

# NOTE FOR FEATURE EXTRACTOR:
# F4 regex in Block 2 must catch two patterns:
#   Pattern A: open('/uploads/' + filename)       -- direct concat in open()
#   Pattern B: path = '/templates/' + name        -- concat on separate line
#              open(path).read()
#
# Updated f4:
#   f4 = int(bool(
#       re.search(r'open\s*\([^)]*\+', code) or
#       re.search(r'=\s*[\'"][/\\][^\'"]*[\'"]\s*\+', code)
#   ))

path_traversal = [

    # ── VULNERABLE (label=1) ──────────────────────

    {"code": "def read_file(filename):\n    with open('/uploads/' + filename) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_template(name):\n    path = '/templates/' + name + '.html'\n    return open(path).read()", "label": 1, "type": "path_traversal"},

    {"code": "def serve_file(filepath):\n    with open('/static/' + filepath, 'rb') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def load_config(config_name):\n    return open('/configs/' + config_name).read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_user_file(username, filename):\n    path = '/home/' + username + '/' + filename\n    with open(path) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def read_log(log_name):\n    with open('/var/logs/' + log_name) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_report(report_id):\n    path = '/reports/' + report_id + '.pdf'\n    return open(path, 'rb').read()", "label": 1, "type": "path_traversal"},

    {"code": "def load_image(image_name):\n    return open('/images/' + image_name, 'rb').read()", "label": 1, "type": "path_traversal"},

    {"code": "def read_data(data_file):\n    with open('/data/' + data_file) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_document(doc_name):\n    path = '/documents/' + doc_name\n    with open(path) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def load_plugin(plugin_name):\n    with open('/plugins/' + plugin_name + '.py') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_backup(backup_file):\n    return open('/backups/' + backup_file, 'rb').read()", "label": 1, "type": "path_traversal"},

    {"code": "def read_certificate(cert_name):\n    with open('/certs/' + cert_name) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def load_script(script_name):\n    path = '/scripts/' + script_name\n    return open(path).read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_asset(asset_path):\n    with open('/assets/' + asset_path, 'rb') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def read_profile(username):\n    with open('/profiles/' + username + '.json') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_invoice(invoice_id):\n    path = '/invoices/' + invoice_id + '.txt'\n    return open(path).read()", "label": 1, "type": "path_traversal"},

    {"code": "def load_theme(theme_name):\n    return open('/themes/' + theme_name + '/style.css').read()", "label": 1, "type": "path_traversal"},

    {"code": "def read_key(key_name):\n    with open('/keys/' + key_name) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def get_export(export_file):\n    with open('/exports/' + export_file) as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    {"code": "def load_schema(schema_name):\n    path = '/schemas/' + schema_name + '.json'\n    return open(path).read()", "label": 1, "type": "path_traversal"},

    # NEW: Flask request context — real download endpoint vulnerability
    {"code": "def download(request):\n    filename = request.args.get('file')\n    with open('/uploads/' + filename, 'rb') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    # NEW: f-string path — modern Python vulnerable pattern
    {"code": "def get_user_data(user_id):\n    with open(f'/data/users/{user_id}.json') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    # NEW: class method context
    {"code": "class FileServer:\n    def serve(self, filename):\n        with open('/public/' + filename, 'rb') as f:\n            return f.read()", "label": 1, "type": "path_traversal"},

    # NEW: os.path.join still vulnerable if base is not enforced
    {"code": "def get_attachment(base_dir, filename):\n    path = os.path.join(base_dir, filename)\n    with open(path, 'rb') as f:\n        return f.read()", "label": 1, "type": "path_traversal"},

    # ── SAFE (label=0) ────────────────────────────

    {"code": "def read_file(filename):\n    safe = os.path.basename(filename)\n    with open(os.path.join('/uploads', safe)) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def get_template(name):\n    allowed = ['home', 'about', 'contact']\n    if name not in allowed:\n        raise ValueError('Invalid template')\n    return open(f'/templates/{name}.html').read()", "label": 0, "type": "safe"},

    {"code": "def serve_file(filepath):\n    base = '/static'\n    full = os.path.realpath(os.path.join(base, filepath))\n    if not full.startswith(base + '/'):\n        raise ValueError('Access denied')\n    return open(full, 'rb').read()", "label": 0, "type": "safe"},

    {"code": "def load_config(config_name):\n    allowed = ['app', 'db', 'cache']\n    if config_name not in allowed:\n        raise ValueError('Config not allowed')\n    return open(f'/configs/{config_name}').read()", "label": 0, "type": "safe"},

    {"code": "def get_user_file(username, filename):\n    safe_user = os.path.basename(username)\n    safe_file = os.path.basename(filename)\n    path = os.path.join('/home', safe_user, safe_file)\n    with open(path) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def read_log(log_name):\n    safe = os.path.basename(log_name)\n    with open(os.path.join('/var/logs', safe)) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def get_report(report_id):\n    if not report_id.isalnum():\n        raise ValueError('Invalid report id')\n    return open(f'/reports/{report_id}.pdf', 'rb').read()", "label": 0, "type": "safe"},

    {"code": "def load_image(image_name):\n    safe = os.path.basename(image_name)\n    return open(os.path.join('/images', safe), 'rb').read()", "label": 0, "type": "safe"},

    {"code": "def read_data(data_file):\n    safe = os.path.basename(data_file)\n    with open(os.path.join('/data', safe)) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def get_document(doc_name):\n    base = '/documents'\n    full = os.path.realpath(os.path.join(base, doc_name))\n    if not full.startswith(base + '/'):\n        raise ValueError('Access denied')\n    with open(full) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def load_plugin(plugin_name):\n    allowed = ['auth', 'cache', 'logger']\n    if plugin_name not in allowed:\n        raise ValueError('Plugin not allowed')\n    with open(f'/plugins/{plugin_name}.py') as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def get_backup(backup_file):\n    safe = os.path.basename(backup_file)\n    return open(os.path.join('/backups', safe), 'rb').read()", "label": 0, "type": "safe"},

    {"code": "def read_certificate(cert_name):\n    if not cert_name.replace('-','').replace('_','').isalnum():\n        raise ValueError('Invalid cert name')\n    with open(f'/certs/{cert_name}') as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def load_script(script_name):\n    allowed = ['deploy', 'test', 'lint']\n    if script_name not in allowed:\n        raise ValueError('Script not allowed')\n    return open(f'/scripts/{script_name}').read()", "label": 0, "type": "safe"},

    {"code": "def get_asset(asset_path):\n    base = '/assets'\n    full = os.path.realpath(os.path.join(base, asset_path))\n    if not full.startswith(base + '/'):\n        raise ValueError('Access denied')\n    with open(full, 'rb') as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def read_profile(username):\n    if not username.isalnum():\n        raise ValueError('Invalid username')\n    with open(f'/profiles/{username}.json') as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def get_invoice(invoice_id):\n    if not invoice_id.isalnum():\n        raise ValueError('Invalid invoice id')\n    return open(f'/invoices/{invoice_id}.txt').read()", "label": 0, "type": "safe"},

    {"code": "def load_theme(theme_name):\n    allowed = ['light', 'dark', 'blue']\n    if theme_name not in allowed:\n        raise ValueError('Theme not allowed')\n    return open(f'/themes/{theme_name}/style.css').read()", "label": 0, "type": "safe"},

    {"code": "def read_key(key_name):\n    safe = os.path.basename(key_name)\n    with open(os.path.join('/keys', safe)) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def get_export(export_file):\n    safe = os.path.basename(export_file)\n    with open(os.path.join('/exports', safe)) as f:\n        return f.read()", "label": 0, "type": "safe"},

    {"code": "def load_schema(schema_name):\n    allowed = ['user', 'product', 'order']\n    if schema_name not in allowed:\n        raise ValueError('Schema not allowed')\n    return open(f'/schemas/{schema_name}.json').read()", "label": 0, "type": "safe"},

    # NEW: safe Flask download — realpath + startswith
    {"code": "def download(request):\n    filename = request.args.get('file')\n    base = '/uploads'\n    full = os.path.realpath(os.path.join(base, filename))\n    if not full.startswith(base + '/'):\n        raise ValueError('Access denied')\n    with open(full, 'rb') as f:\n        return f.read()", "label": 0, "type": "safe"},

    # NEW: safe f-string — validate user_id is numeric
    {"code": "def get_user_data(user_id):\n    if not str(user_id).isdigit():\n        raise ValueError('Invalid user id')\n    with open(f'/data/users/{user_id}.json') as f:\n        return f.read()", "label": 0, "type": "safe"},

    # NEW: safe class method using pathlib — modern Python standard
    {"code": "class FileServer:\n    BASE = '/public'\n    def serve(self, filename):\n        from pathlib import Path\n        safe = Path(self.BASE) / Path(filename).name\n        if not str(safe.resolve()).startswith(self.BASE):\n            raise ValueError('Access denied')\n        return safe.read_bytes()", "label": 0, "type": "safe"},

    # NEW: safe os.path.join with realpath enforcement
    {"code": "def get_attachment(base_dir, filename):\n    base = os.path.realpath('/attachments')\n    full = os.path.realpath(os.path.join(base, os.path.basename(filename)))\n    if not full.startswith(base + '/'):\n        raise ValueError('Access denied')\n    with open(full, 'rb') as f:\n        return f.read()", "label": 0, "type": "safe"},
]

script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'path_traversal.json')
with open(save_path, 'w') as f:
    json.dump(path_traversal, f, indent=2)

print(f"Saved: {save_path}")
print(f"Total:      {len(path_traversal)}")
print(f"Vulnerable: {sum(1 for e in path_traversal if e['label'] == 1)}")
print(f"Safe:       {sum(1 for e in path_traversal if e['label'] == 0)}")
# %%