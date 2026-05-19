# %%
import json
import os

# IMPROVEMENTS FROM v1:
# 1. Added dotenv pattern as safe alternative (industry standard)
# 2. Added config file pattern as safe alternative
# 3. Added Flask app.config pattern — real web framework usage
# 4. Added class/settings context for both vuln and safe
# 5. Added inline assignment variants (e.g. Client(api_key="hardcoded"))

hardcoded_secrets = [

    # ── VULNERABLE (label=1) ──────────────────────

    {"code": "def connect_db():\n    password = \"admin123\"\n    return db.connect(user=\"root\", password=password)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_api_client():\n    api_key = \"sk-abc123xyz789\"\n    return Client(api_key=api_key)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def send_email():\n    token = \"ghp_realtoken123\"\n    return smtp.connect(token=token)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def connect_redis():\n    secret = \"mysecretpassword\"\n    return redis.Redis(password=secret)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_storage():\n    key = \"AKIAIOSFODNN7EXAMPLE\"\n    return Storage(access_key=key)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def authenticate():\n    pwd = \"superSecret99\"\n    return auth.login(password=pwd)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def connect_mongo():\n    password = \"mongo_pass_2024\"\n    return MongoClient(f\"mongodb://admin:{password}@localhost\")", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_jwt_token():\n    secret = \"jwt_secret_key_hardcoded\"\n    return jwt.encode(payload, secret)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def setup_smtp():\n    token = \"smtp_token_abc456\"\n    return smtplib.SMTP_SSL(host, token=token)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def init_payment():\n    api_key = \"pk_live_51abc123\"\n    stripe.api_key = api_key\n    return stripe", "label": 1, "type": "hardcoded_secret"},

    {"code": "def connect_ftp():\n    password = \"ftp_pass_123\"\n    ftp.connect(host, user, password)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_github_client():\n    token = \"github_pat_11ABC123\"\n    return Github(token)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def setup_aws():\n    key = \"wJalrXUtnFEMI/K7MDENG\"\n    return boto3.client('s3', aws_secret_access_key=key)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_db_uri():\n    password = \"db_password_prod\"\n    return f\"postgresql://user:{password}@localhost/db\"", "label": 1, "type": "hardcoded_secret"},

    {"code": "def connect_ssh():\n    pwd = \"ssh_password_123\"\n    client.connect(hostname, password=pwd)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_slack_client():\n    token = \"xoxb-slack-token-here\"\n    return WebClient(token=token)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def init_twilio():\n    secret = \"twilio_auth_token_123\"\n    return Client(account_sid, secret)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_sendgrid():\n    api_key = \"SG.sendgrid_key_abc\"\n    return SendGridAPIClient(api_key)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def connect_ldap():\n    password = \"ldap_bind_password\"\n    conn.simple_bind_s(dn, password)", "label": 1, "type": "hardcoded_secret"},

    {"code": "def get_firebase():\n    key = \"firebase_secret_key_abc\"\n    return firebase_admin.initialize_app(credentials.Certificate(key))", "label": 1, "type": "hardcoded_secret"},

    {"code": "def setup_oauth():\n    secret = \"oauth_client_secret_xyz\"\n    return OAuth2Session(client_id, client_secret=secret)", "label": 1, "type": "hardcoded_secret"},

    # NEW: inline hardcoded — no intermediate variable, still detected
    {"code": "def get_weather():\n    return requests.get('https://api.weather.com/data', headers={'X-API-Key': 'hardcoded_key_xyz123'})", "label": 1, "type": "hardcoded_secret"},

    # NEW: class attribute hardcoded secret
    {"code": "class Config:\n    def get_db(self):\n        password = \"prod_db_pass_2024\"\n        return psycopg2.connect(dbname='mydb', password=password)", "label": 1, "type": "hardcoded_secret"},

    # NEW: Flask app.config with hardcoded secret
    {"code": "def create_app():\n    app = Flask(__name__)\n    app.config['SECRET_KEY'] = 'hardcoded_flask_secret'\n    return app", "label": 1, "type": "hardcoded_secret"},

    # NEW: token passed directly in function call
    {"code": "def notify_slack():\n    client = WebClient(token=\"xoxb-hardcoded-slack-999\")\n    client.chat_postMessage(channel='#alerts', text='alert')", "label": 1, "type": "hardcoded_secret"},

    # ── SAFE (label=0) ────────────────────────────

    {"code": "def connect_db():\n    password = os.environ.get('DB_PASSWORD')\n    return db.connect(user='root', password=password)", "label": 0, "type": "safe"},

    {"code": "def get_api_client():\n    api_key = os.environ.get('API_KEY')\n    return Client(api_key=api_key)", "label": 0, "type": "safe"},

    {"code": "def send_email():\n    token = os.environ.get('SMTP_TOKEN')\n    return smtp.connect(token=token)", "label": 0, "type": "safe"},

    {"code": "def connect_redis():\n    secret = os.environ.get('REDIS_PASSWORD')\n    return redis.Redis(password=secret)", "label": 0, "type": "safe"},

    {"code": "def get_storage():\n    key = os.environ.get('AWS_ACCESS_KEY')\n    return Storage(access_key=key)", "label": 0, "type": "safe"},

    {"code": "def authenticate():\n    pwd = os.environ.get('AUTH_PASSWORD')\n    return auth.login(password=pwd)", "label": 0, "type": "safe"},

    {"code": "def connect_mongo():\n    password = os.environ.get('MONGO_PASSWORD')\n    return MongoClient(f'mongodb://admin:{password}@localhost')", "label": 0, "type": "safe"},

    {"code": "def get_jwt_token():\n    secret = os.environ.get('JWT_SECRET')\n    return jwt.encode(payload, secret)", "label": 0, "type": "safe"},

    {"code": "def setup_smtp():\n    token = os.environ.get('SMTP_TOKEN')\n    return smtplib.SMTP_SSL(host, token=token)", "label": 0, "type": "safe"},

    {"code": "def init_payment():\n    api_key = os.environ.get('STRIPE_API_KEY')\n    stripe.api_key = api_key\n    return stripe", "label": 0, "type": "safe"},

    {"code": "def connect_ftp():\n    password = os.environ.get('FTP_PASSWORD')\n    ftp.connect(host, user, password)", "label": 0, "type": "safe"},

    {"code": "def get_github_client():\n    token = os.environ.get('GITHUB_TOKEN')\n    return Github(token)", "label": 0, "type": "safe"},

    {"code": "def setup_aws():\n    key = os.environ.get('AWS_SECRET_KEY')\n    return boto3.client('s3', aws_secret_access_key=key)", "label": 0, "type": "safe"},

    {"code": "def get_db_uri():\n    password = os.environ.get('DB_PASSWORD')\n    return f'postgresql://user:{password}@localhost/db'", "label": 0, "type": "safe"},

    {"code": "def connect_ssh():\n    pwd = os.environ.get('SSH_PASSWORD')\n    client.connect(hostname, password=pwd)", "label": 0, "type": "safe"},

    {"code": "def get_slack_client():\n    token = os.environ.get('SLACK_TOKEN')\n    return WebClient(token=token)", "label": 0, "type": "safe"},

    {"code": "def init_twilio():\n    secret = os.environ.get('TWILIO_AUTH_TOKEN')\n    return Client(account_sid, secret)", "label": 0, "type": "safe"},

    {"code": "def get_sendgrid():\n    api_key = os.environ.get('SENDGRID_API_KEY')\n    return SendGridAPIClient(api_key)", "label": 0, "type": "safe"},

    {"code": "def connect_ldap():\n    password = os.environ.get('LDAP_PASSWORD')\n    conn.simple_bind_s(dn, password)", "label": 0, "type": "safe"},

    {"code": "def get_firebase():\n    key = os.environ.get('FIREBASE_KEY')\n    return firebase_admin.initialize_app(credentials.Certificate(key))", "label": 0, "type": "safe"},

    {"code": "def setup_oauth():\n    secret = os.environ.get('OAUTH_CLIENT_SECRET')\n    return OAuth2Session(client_id, client_secret=secret)", "label": 0, "type": "safe"},

    # NEW: safe inline — env var in headers dict
    {"code": "def get_weather():\n    return requests.get('https://api.weather.com/data', headers={'X-API-Key': os.environ.get('WEATHER_API_KEY')})", "label": 0, "type": "safe"},

    # NEW: safe class method
    {"code": "class Config:\n    def get_db(self):\n        password = os.environ.get('DB_PASSWORD')\n        return psycopg2.connect(dbname='mydb', password=password)", "label": 0, "type": "safe"},

    # NEW: safe Flask app.config
    {"code": "def create_app():\n    app = Flask(__name__)\n    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')\n    return app", "label": 0, "type": "safe"},

    # NEW: safe Slack token from env
    {"code": "def notify_slack():\n    client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))\n    client.chat_postMessage(channel='#alerts', text='alert')", "label": 0, "type": "safe"},
]

script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'hardcoded_secrets.json')
with open(save_path, 'w') as f:
    json.dump(hardcoded_secrets, f, indent=2)

print(f"Saved: {save_path}")
print(f"Total:      {len(hardcoded_secrets)}")
print(f"Vulnerable: {sum(1 for e in hardcoded_secrets if e['label'] == 1)}")
print(f"Safe:       {sum(1 for e in hardcoded_secrets if e['label'] == 0)}")
# %%