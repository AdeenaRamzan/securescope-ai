# %%
import json
import os

# IMPROVEMENTS FROM v1:
# 1. Added Flask/web request context (3 entries) — real web app scenario
# 2. Added class method context (2 entries)
# 3. Added os.popen() injection — another real vulnerable pattern
# 4. Added subprocess.Popen with shell=True — missed in v1
# 5. Safe: added more validation diversity (regex, isalnum, allowlist)

command_injection = [

    # ── VULNERABLE (label=1) ──────────────────────

    {"code": "def ping(host):\n    os.system('ping ' + host)\n    return 'done'", "label": 1, "type": "cmd_injection"},

    {"code": "def convert_file(filename):\n    subprocess.call('convert ' + filename + ' output.png', shell=True)\n    return 'converted'", "label": 1, "type": "cmd_injection"},

    {"code": "def run_scan(target):\n    os.system('nmap ' + target)\n    return 'scan complete'", "label": 1, "type": "cmd_injection"},

    {"code": "def compress(filepath):\n    os.system('zip output.zip ' + filepath)", "label": 1, "type": "cmd_injection"},

    {"code": "def backup_db(db_name):\n    os.system('pg_dump ' + db_name + ' > backup.sql')", "label": 1, "type": "cmd_injection"},

    {"code": "def resize_image(filename, size):\n    subprocess.call('convert ' + filename + ' -resize ' + size, shell=True)", "label": 1, "type": "cmd_injection"},

    {"code": "def run_test(test_name):\n    os.system('pytest ' + test_name)\n    return 'tests done'", "label": 1, "type": "cmd_injection"},

    {"code": "def send_file(dest, filename):\n    os.system('scp ' + filename + ' ' + dest)", "label": 1, "type": "cmd_injection"},

    {"code": "def lookup_dns(domain):\n    os.system('nslookup ' + domain)\n    return 'lookup done'", "label": 1, "type": "cmd_injection"},

    {"code": "def traceroute(host):\n    subprocess.call('traceroute ' + host, shell=True)", "label": 1, "type": "cmd_injection"},

    {"code": "def compile_code(filename):\n    os.system('gcc ' + filename + ' -o output')", "label": 1, "type": "cmd_injection"},

    {"code": "def run_migration(script):\n    os.system('python ' + script)\n    return 'migrated'", "label": 1, "type": "cmd_injection"},

    {"code": "def list_dir(path):\n    os.system('ls ' + path)\n    return 'listed'", "label": 1, "type": "cmd_injection"},

    {"code": "def delete_file(filepath):\n    os.system('rm ' + filepath)", "label": 1, "type": "cmd_injection"},

    {"code": "def run_curl(url):\n    os.system('curl ' + url)\n    return 'fetched'", "label": 1, "type": "cmd_injection"},

    {"code": "def extract_archive(filename):\n    subprocess.call('tar -xf ' + filename, shell=True)", "label": 1, "type": "cmd_injection"},

    {"code": "def run_deploy(env):\n    os.system('deploy.sh ' + env)\n    return 'deployed'", "label": 1, "type": "cmd_injection"},

    {"code": "def check_port(host, port):\n    os.system('nc -zv ' + host + ' ' + port)", "label": 1, "type": "cmd_injection"},

    {"code": "def generate_report(report_id):\n    subprocess.call('generate_report.sh ' + report_id, shell=True)", "label": 1, "type": "cmd_injection"},

    {"code": "def run_linter(filename):\n    os.system('pylint ' + filename)", "label": 1, "type": "cmd_injection"},

    {"code": "def process_video(filename):\n    subprocess.call('ffmpeg -i ' + filename + ' output.mp4', shell=True)", "label": 1, "type": "cmd_injection"},

    # NEW: os.popen — real vulnerable pattern missed in v1
    {"code": "def get_disk_usage(path):\n    result = os.popen('du -sh ' + path).read()\n    return result", "label": 1, "type": "cmd_injection"},

    # NEW: subprocess.Popen with shell=True — missed in v1
    {"code": "def run_script(script_name):\n    proc = subprocess.Popen('bash ' + script_name, shell=True)\n    proc.wait()", "label": 1, "type": "cmd_injection"},

    # NEW: Flask request context — real web vulnerability
    {"code": "def scan_host(request):\n    host = request.form.get('host')\n    os.system('ping -c 1 ' + host)\n    return 'done'", "label": 1, "type": "cmd_injection"},

    # NEW: class method context
    {"code": "class FileProcessor:\n    def convert(self, filename):\n        os.system('convert ' + filename + ' output.jpg')", "label": 1, "type": "cmd_injection"},

    # ── SAFE (label=0) ────────────────────────────

    {"code": "def ping(host):\n    subprocess.run(['ping', '-c', '1', host], capture_output=True)\n    return 'done'", "label": 0, "type": "safe"},

    {"code": "def convert_file(filename):\n    safe = os.path.basename(filename)\n    subprocess.run(['convert', safe, 'output.png'])\n    return 'converted'", "label": 0, "type": "safe"},

    {"code": "def run_scan(target):\n    if not re.match(r'^[a-zA-Z0-9.-]+$', target):\n        raise ValueError('Invalid target')\n    subprocess.run(['nmap', target])\n    return 'scan complete'", "label": 0, "type": "safe"},

    {"code": "def compress(filepath):\n    safe = os.path.basename(filepath)\n    subprocess.run(['zip', 'output.zip', safe])", "label": 0, "type": "safe"},

    {"code": "def backup_db(db_name):\n    if not db_name.isalnum():\n        raise ValueError('Invalid db name')\n    with open('backup.sql', 'w') as f:\n        subprocess.run(['pg_dump', db_name], stdout=f)", "label": 0, "type": "safe"},

    {"code": "def resize_image(filename, size):\n    safe_file = os.path.basename(filename)\n    if not re.match(r'^\\d+x\\d+$', size):\n        raise ValueError('Invalid size format')\n    subprocess.run(['convert', safe_file, '-resize', size])", "label": 0, "type": "safe"},

    {"code": "def run_test(test_name):\n    allowed = ['test_auth', 'test_api', 'test_db']\n    if test_name not in allowed:\n        raise ValueError('Test not allowed')\n    subprocess.run(['pytest', test_name])\n    return 'tests done'", "label": 0, "type": "safe"},

    {"code": "def send_file(dest, filename):\n    safe_file = os.path.basename(filename)\n    subprocess.run(['scp', safe_file, dest])", "label": 0, "type": "safe"},

    {"code": "def lookup_dns(domain):\n    if not re.match(r'^[a-zA-Z0-9.-]+$', domain):\n        raise ValueError('Invalid domain')\n    subprocess.run(['nslookup', domain])", "label": 0, "type": "safe"},

    {"code": "def traceroute(host):\n    if not re.match(r'^[a-zA-Z0-9.-]+$', host):\n        raise ValueError('Invalid host')\n    subprocess.run(['traceroute', host])", "label": 0, "type": "safe"},

    {"code": "def compile_code(filename):\n    safe = os.path.basename(filename)\n    subprocess.run(['gcc', safe, '-o', 'output'])", "label": 0, "type": "safe"},

    {"code": "def run_migration(script):\n    allowed = ['001_init', '002_users', '003_orders']\n    if script not in allowed:\n        raise ValueError('Migration not allowed')\n    subprocess.run(['python', script])\n    return 'migrated'", "label": 0, "type": "safe"},

    {"code": "def list_dir(path):\n    safe = os.path.realpath(path)\n    if not safe.startswith('/allowed/base'):\n        raise ValueError('Access denied')\n    return os.listdir(safe)", "label": 0, "type": "safe"},

    {"code": "def delete_file(filepath):\n    safe = os.path.realpath(filepath)\n    if not safe.startswith('/uploads'):\n        raise ValueError('Cannot delete outside uploads')\n    os.remove(safe)", "label": 0, "type": "safe"},

    {"code": "def run_curl(url):\n    import urllib.request\n    return urllib.request.urlopen(url).read()", "label": 0, "type": "safe"},

    {"code": "def extract_archive(filename):\n    safe = os.path.basename(filename)\n    subprocess.run(['tar', '-xf', safe])", "label": 0, "type": "safe"},

    {"code": "def run_deploy(env):\n    allowed = ['staging', 'production', 'dev']\n    if env not in allowed:\n        raise ValueError('Invalid environment')\n    subprocess.run(['deploy.sh', env])\n    return 'deployed'", "label": 0, "type": "safe"},

    {"code": "def check_port(host, port):\n    import socket\n    sock = socket.socket()\n    result = sock.connect_ex((host, int(port)))\n    sock.close()\n    return result == 0", "label": 0, "type": "safe"},

    {"code": "def generate_report(report_id):\n    if not report_id.isalnum():\n        raise ValueError('Invalid report id')\n    subprocess.run(['generate_report.sh', report_id])", "label": 0, "type": "safe"},

    {"code": "def run_linter(filename):\n    safe = os.path.basename(filename)\n    subprocess.run(['pylint', safe])", "label": 0, "type": "safe"},

    {"code": "def process_video(filename):\n    safe = os.path.basename(filename)\n    subprocess.run(['ffmpeg', '-i', safe, 'output.mp4'])", "label": 0, "type": "safe"},

    # NEW: safe os.popen alternative — use subprocess with list
    {"code": "def get_disk_usage(path):\n    safe = os.path.realpath(path)\n    if not safe.startswith('/data'):\n        raise ValueError('Access denied')\n    result = subprocess.run(['du', '-sh', safe], capture_output=True, text=True)\n    return result.stdout", "label": 0, "type": "safe"},

    # NEW: safe Popen alternative
    {"code": "def run_script(script_name):\n    allowed = ['cleanup.sh', 'backup.sh', 'report.sh']\n    if script_name not in allowed:\n        raise ValueError('Script not allowed')\n    proc = subprocess.Popen(['bash', script_name])\n    proc.wait()", "label": 0, "type": "safe"},

    # NEW: safe Flask request context
    {"code": "def scan_host(request):\n    host = request.form.get('host')\n    if not re.match(r'^[a-zA-Z0-9.-]+$', host):\n        raise ValueError('Invalid host')\n    subprocess.run(['ping', '-c', '1', host], capture_output=True)\n    return 'done'", "label": 0, "type": "safe"},

    # NEW: safe class method
    {"code": "class FileProcessor:\n    def convert(self, filename):\n        safe = os.path.basename(filename)\n        subprocess.run(['convert', safe, 'output.jpg'])", "label": 0, "type": "safe"},
]

script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'command_injection.json')
with open(save_path, 'w') as f:
    json.dump(command_injection, f, indent=2)

print(f"Saved: {save_path}")
print(f"Total:      {len(command_injection)}")
print(f"Vulnerable: {sum(1 for e in command_injection if e['label'] == 1)}")
print(f"Safe:       {sum(1 for e in command_injection if e['label'] == 0)}")
# %%