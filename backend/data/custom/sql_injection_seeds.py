# %%
import json
import os



sql_injection = [

    # ── VULNERABLE (label=1) ──────────────────────

    # FIX: added quotes around id — was syntax error not injection
    {"code": "def get_user(user_id):\n    query = \"SELECT * FROM users WHERE id = '\" + user_id + \"'\"\n    return db.execute(query)", "label": 1, "type": "sql_injection"},

    {"code": "def find_product(name):\n    sql = \"SELECT * FROM products WHERE name = '\" + name + \"'\"\n    return cursor.execute(sql)", "label": 1, "type": "sql_injection"},

    {"code": "def get_orders(customer):\n    q = \"SELECT * FROM orders WHERE customer = '\" + customer + \"'\"\n    conn.execute(q)\n    return conn.fetchall()", "label": 1, "type": "sql_injection"},

    {"code": "def search_users(email):\n    query = \"SELECT id, name FROM users WHERE email = '\" + email + \"'\"\n    return db.execute(query).fetchone()", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around post_id
    {"code": "def get_post(post_id):\n    return db.execute(\"SELECT * FROM posts WHERE id = '\" + post_id + \"'\")", "label": 1, "type": "sql_injection"},

    {"code": "def login(username, password):\n    sql = \"SELECT * FROM users WHERE username = '\" + username + \"' AND password = '\" + password + \"'\"\n    return cursor.execute(sql)", "label": 1, "type": "sql_injection"},

    {"code": "def filter_by_status(status):\n    query = \"SELECT * FROM tasks WHERE status = '\" + status + \"'\"\n    db.execute(query)\n    return db.fetchall()", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around emp_id
    {"code": "def get_employee(emp_id):\n    sql = \"SELECT name, salary FROM employees WHERE id = '\" + emp_id + \"'\"\n    return cursor.execute(sql).fetchone()", "label": 1, "type": "sql_injection"},

    {"code": "def search_logs(keyword):\n    q = \"SELECT * FROM logs WHERE message LIKE '%\" + keyword + \"%'\"\n    return db.execute(q).fetchall()", "label": 1, "type": "sql_injection"},

    {"code": "def get_category(cat_name):\n    query = \"SELECT * FROM categories WHERE name = '\" + cat_name + \"'\"\n    return conn.execute(query)", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around user_id
    {"code": "def delete_user(user_id):\n    db.execute(\"DELETE FROM users WHERE id = '\" + user_id + \"'\")", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around user_id in WHERE clause
    {"code": "def update_email(user_id, email):\n    sql = \"UPDATE users SET email = '\" + email + \"' WHERE id = '\" + user_id + \"'\"\n    db.execute(sql)", "label": 1, "type": "sql_injection"},

    {"code": "def get_report(report_type):\n    query = \"SELECT * FROM reports WHERE type = '\" + report_type + \"'\"\n    return cursor.execute(query).fetchall()", "label": 1, "type": "sql_injection"},

    {"code": "def find_by_username(username):\n    return db.execute(\"SELECT * FROM accounts WHERE username = '\" + username + \"'\")", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around account_id
    {"code": "def get_transactions(account_id):\n    sql = \"SELECT * FROM transactions WHERE account_id = '\" + account_id + \"'\"\n    return cursor.execute(sql).fetchall()", "label": 1, "type": "sql_injection"},

    {"code": "def search_items(query_str):\n    sql = \"SELECT * FROM items WHERE title LIKE '%\" + query_str + \"%'\"\n    return db.execute(sql)", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around post_id
    {"code": "def get_comments(post_id):\n    q = \"SELECT * FROM comments WHERE post_id = '\" + post_id + \"'\"\n    cursor.execute(q)\n    return cursor.fetchall()", "label": 1, "type": "sql_injection"},

    {"code": "def get_invoice(invoice_num):\n    return conn.execute(\"SELECT * FROM invoices WHERE number = '\" + invoice_num + \"'\")", "label": 1, "type": "sql_injection"},

    {"code": "def find_customer(phone):\n    sql = \"SELECT * FROM customers WHERE phone = '\" + phone + \"'\"\n    return db.execute(sql).fetchone()", "label": 1, "type": "sql_injection"},

    {"code": "def get_schedule(day):\n    query = \"SELECT * FROM schedule WHERE day = '\" + day + \"'\"\n    return cursor.execute(query).fetchall()", "label": 1, "type": "sql_injection"},

    # FIX: added quotes around sensor_id
    {"code": "def get_sensor_data(sensor_id):\n    sql = \"SELECT * FROM sensors WHERE id = '\" + sensor_id + \"'\"\n    return db.execute(sql).fetchall()", "label": 1, "type": "sql_injection"},

    # NEW: f-string injection — very common modern Python pattern
    {"code": "def get_product_by_sku(sku):\n    return db.execute(f\"SELECT * FROM products WHERE sku = '{sku}'\")", "label": 1, "type": "sql_injection"},

    # NEW: f-string in realistic function
    {"code": "def get_user_profile(username):\n    result = db.execute(f\"SELECT * FROM profiles WHERE username = '{username}'\")\n    return result.fetchone()", "label": 1, "type": "sql_injection"},

    # NEW: Flask request.args — real web app vulnerability
    {"code": "def search(request):\n    term = request.args.get('q')\n    rows = db.execute(\"SELECT * FROM posts WHERE title LIKE '%\" + term + \"%'\")\n    return rows.fetchall()", "label": 1, "type": "sql_injection"},

    # NEW: class method context — ORM-style usage
    {"code": "class UserRepository:\n    def find_by_email(self, email):\n        sql = \"SELECT * FROM users WHERE email = '\" + email + \"'\"\n        return self.db.execute(sql).fetchone()", "label": 1, "type": "sql_injection"},

    # ── SAFE (label=0) ───────────────────────────

    {"code": "def get_user(user_id):\n    query = \"SELECT * FROM users WHERE id = ?\"\n    return db.execute(query, (user_id,))", "label": 0, "type": "safe"},

    {"code": "def find_product(name):\n    cursor.execute(\"SELECT * FROM products WHERE name = ?\", (name,))\n    return cursor.fetchall()", "label": 0, "type": "safe"},

    {"code": "def get_orders(customer):\n    q = \"SELECT * FROM orders WHERE customer = ?\"\n    conn.execute(q, (customer,))\n    return conn.fetchall()", "label": 0, "type": "safe"},

    {"code": "def search_users(email):\n    query = \"SELECT id, name FROM users WHERE email = ?\"\n    return db.execute(query, (email,)).fetchone()", "label": 0, "type": "safe"},

    {"code": "def get_post(post_id):\n    return db.execute(\"SELECT * FROM posts WHERE id = ?\", (post_id,))", "label": 0, "type": "safe"},

    {"code": "def login(username, password):\n    sql = \"SELECT * FROM users WHERE username = ? AND password = ?\"\n    return cursor.execute(sql, (username, password))", "label": 0, "type": "safe"},

    {"code": "def filter_by_status(status):\n    query = \"SELECT * FROM tasks WHERE status = ?\"\n    db.execute(query, (status,))\n    return db.fetchall()", "label": 0, "type": "safe"},

    {"code": "def get_employee(emp_id):\n    sql = \"SELECT name, salary FROM employees WHERE id = ?\"\n    return cursor.execute(sql, (emp_id,)).fetchone()", "label": 0, "type": "safe"},

    # IMPROVED: LIKE uses ? placeholder with f-string in tuple
    {"code": "def search_logs(keyword):\n    q = \"SELECT * FROM logs WHERE message LIKE ?\"\n    return db.execute(q, (f'%{keyword}%',)).fetchall()", "label": 0, "type": "safe"},

    {"code": "def get_category(cat_name):\n    query = \"SELECT * FROM categories WHERE name = ?\"\n    return conn.execute(query, (cat_name,))", "label": 0, "type": "safe"},

    {"code": "def delete_user(user_id):\n    db.execute(\"DELETE FROM users WHERE id = ?\", (user_id,))", "label": 0, "type": "safe"},

    {"code": "def update_email(user_id, email):\n    sql = \"UPDATE users SET email = ? WHERE id = ?\"\n    db.execute(sql, (email, user_id))", "label": 0, "type": "safe"},

    {"code": "def get_report(report_type):\n    query = \"SELECT * FROM reports WHERE type = ?\"\n    return cursor.execute(query, (report_type,)).fetchall()", "label": 0, "type": "safe"},

    {"code": "def find_by_username(username):\n    return db.execute(\"SELECT * FROM accounts WHERE username = ?\", (username,))", "label": 0, "type": "safe"},

    {"code": "def get_transactions(account_id):\n    sql = \"SELECT * FROM transactions WHERE account_id = ?\"\n    return cursor.execute(sql, (account_id,)).fetchall()", "label": 0, "type": "safe"},

    # IMPROVED: LIKE uses ? placeholder
    {"code": "def search_items(query_str):\n    sql = \"SELECT * FROM items WHERE title LIKE ?\"\n    return db.execute(sql, (f'%{query_str}%',))", "label": 0, "type": "safe"},

    {"code": "def get_comments(post_id):\n    q = \"SELECT * FROM comments WHERE post_id = ?\"\n    cursor.execute(q, (post_id,))\n    return cursor.fetchall()", "label": 0, "type": "safe"},

    {"code": "def get_invoice(invoice_num):\n    return conn.execute(\"SELECT * FROM invoices WHERE number = ?\", (invoice_num,))", "label": 0, "type": "safe"},

    {"code": "def find_customer(phone):\n    sql = \"SELECT * FROM customers WHERE phone = ?\"\n    return db.execute(sql, (phone,)).fetchone()", "label": 0, "type": "safe"},

    {"code": "def get_schedule(day):\n    query = \"SELECT * FROM schedule WHERE day = ?\"\n    return cursor.execute(query, (day,)).fetchall()", "label": 0, "type": "safe"},

    {"code": "def get_sensor_data(sensor_id):\n    sql = \"SELECT * FROM sensors WHERE id = ?\"\n    return db.execute(sql, (sensor_id,)).fetchall()", "label": 0, "type": "safe"},

    # NEW: safe f-string equivalent
    {"code": "def get_product_by_sku(sku):\n    return db.execute(\"SELECT * FROM products WHERE sku = ?\", (sku,))", "label": 0, "type": "safe"},

    # NEW: safe user profile
    {"code": "def get_user_profile(username):\n    result = db.execute(\"SELECT * FROM profiles WHERE username = ?\", (username,))\n    return result.fetchone()", "label": 0, "type": "safe"},

    # NEW: safe Flask request.args
    {"code": "def search(request):\n    term = request.args.get('q')\n    rows = db.execute(\"SELECT * FROM posts WHERE title LIKE ?\", (f'%{term}%',))\n    return rows.fetchall()", "label": 0, "type": "safe"},

    # NEW: safe class method
    {"code": "class UserRepository:\n    def find_by_email(self, email):\n        sql = \"SELECT * FROM users WHERE email = ?\"\n        return self.db.execute(sql, (email,)).fetchone()", "label": 0, "type": "safe"},

    # ── SAFE: static literal SQL (no user input, no dynamic query) ──
    {"code": "def list_products():\n    cursor.execute(\"SELECT * FROM products\")\n    return cursor.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def list_users():\n    cursor.execute(\"SELECT id, name FROM users\")\n    return cursor.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def list_orders():\n    db.execute(\"SELECT * FROM orders\")\n    return db.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def count_products():\n    cursor.execute(\"SELECT COUNT(*) FROM products\")\n    return cursor.fetchone()[0]", "label": 0, "type": "safe_static_sql"},

    {"code": "def get_active_products():\n    return conn.execute(\"SELECT * FROM products WHERE active = 1\").fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def list_categories():\n    cursor.execute(\"SELECT * FROM categories ORDER BY name\")\n    return cursor.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def fetch_all_posts():\n    db.execute(\"SELECT * FROM posts\")\n    return db.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def list_inventory():\n    cursor.execute(\"SELECT sku, quantity FROM inventory\")\n    return cursor.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def get_default_settings():\n    return db.execute(\"SELECT * FROM settings WHERE is_default = 1\").fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def list_employees():\n    conn.execute(\"SELECT id, name, department FROM employees\")\n    return conn.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def purge_expired_sessions():\n    cursor.execute(\"DELETE FROM sessions WHERE expires_at < NOW()\")\n    return cursor.rowcount", "label": 0, "type": "safe_static_sql"},

    {"code": "def seed_admin_role():\n    db.execute(\"INSERT INTO roles (name) VALUES ('admin')\")\n    return db.commit()", "label": 0, "type": "safe_static_sql"},

    {"code": "class ProductRepository:\n    def list_all(self):\n        self.db.execute(\"SELECT * FROM products\")\n        return self.db.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def refresh_materialized_view():\n    cursor.execute(\"REFRESH MATERIALIZED VIEW sales_summary\")\n    return None", "label": 0, "type": "safe_static_sql"},

    {"code": "def list_audit_logs():\n    query = \"SELECT * FROM audit_logs ORDER BY created_at DESC\"\n    cursor.execute(query)\n    return cursor.fetchall()", "label": 0, "type": "safe_static_sql"},

    {"code": "def get_schema_version():\n    return cursor.execute(\"SELECT version FROM schema_migrations\").fetchone()", "label": 0, "type": "safe_static_sql"},
]

# NOTE: sql_injection.json in git has ~550 rows (expanded dataset).
# Do not overwrite it from this seeds-only list. Use train_phase1.py
# merge_static_sql_examples() to append new rows safely.
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'sql_injection_seeds_only.json')
with open(save_path, 'w') as f:
    json.dump(sql_injection, f, indent=2)

print(f"Saved seeds-only file: {save_path}")
print("(Full sql_injection.json is updated by train_phase1.py merge)")
print(f"Total:      {len(sql_injection)}")
print(f"Vulnerable: {sum(1 for e in sql_injection if e['label'] == 1)}")
print(f"Safe:       {sum(1 for e in sql_injection if e['label'] == 0)}")
# %%