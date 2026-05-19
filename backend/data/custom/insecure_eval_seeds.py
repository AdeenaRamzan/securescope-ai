# %%
import json
import os

# IMPROVEMENTS FROM v1:
# 1. Added Flask request context (3 vuln entries) — eval on request data
# 2. Added class method context (2 entries)
# 3. Added compile() builtin — another dangerous eval-like pattern
# 4. Safe: expanded dispatch dict pattern with lambda — industry standard
# 5. Safe: added more ast.literal_eval usage — the correct safe alternative

insecure_eval = [

    # ── VULNERABLE (label=1) ──────────────────────

    {"code": "def calculate(expr):\n    return eval(expr)", "label": 1, "type": "insecure_eval"},

    {"code": "def run_code(user_input):\n    exec(user_input)\n    return 'done'", "label": 1, "type": "insecure_eval"},

    {"code": "def process(formula):\n    result = eval(formula)\n    return result", "label": 1, "type": "insecure_eval"},

    {"code": "def execute_script(script):\n    exec(script)\n    return 'executed'", "label": 1, "type": "insecure_eval"},

    {"code": "def evaluate_expr(expression):\n    return eval(expression)", "label": 1, "type": "insecure_eval"},

    {"code": "def dynamic_calc(user_formula):\n    answer = eval(user_formula)\n    return answer", "label": 1, "type": "insecure_eval"},

    {"code": "def run_user_code(code_string):\n    exec(code_string)\n    return True", "label": 1, "type": "insecure_eval"},

    {"code": "def compute(input_str):\n    val = eval(input_str)\n    return val", "label": 1, "type": "insecure_eval"},

    {"code": "def parse_condition(condition):\n    return eval(condition)", "label": 1, "type": "insecure_eval"},

    {"code": "def run_filter(filter_expr):\n    return eval(filter_expr)", "label": 1, "type": "insecure_eval"},

    {"code": "def execute_transform(transform):\n    exec(transform)\n    return 'ok'", "label": 1, "type": "insecure_eval"},

    {"code": "def eval_template(template):\n    return eval(template)", "label": 1, "type": "insecure_eval"},

    {"code": "def run_macro(macro_code):\n    exec(macro_code)", "label": 1, "type": "insecure_eval"},

    {"code": "def apply_rule(rule):\n    return eval(rule)", "label": 1, "type": "insecure_eval"},

    {"code": "def process_query(query):\n    return eval(query)", "label": 1, "type": "insecure_eval"},

    {"code": "def run_plugin(plugin_code):\n    exec(plugin_code)\n    return 'plugin executed'", "label": 1, "type": "insecure_eval"},

    {"code": "def evaluate_condition(cond_str):\n    result = eval(cond_str)\n    return bool(result)", "label": 1, "type": "insecure_eval"},

    {"code": "def dynamic_import(code):\n    exec(code)\n    return True", "label": 1, "type": "insecure_eval"},

    {"code": "def apply_function(func_str):\n    return eval(func_str)", "label": 1, "type": "insecure_eval"},

    {"code": "def compute_metric(metric_formula):\n    return eval(metric_formula)", "label": 1, "type": "insecure_eval"},

    # NEW: compile() is eval-equivalent — dangerous pattern
    {"code": "def run_dynamic(code_str):\n    compiled = compile(code_str, '<string>', 'exec')\n    exec(compiled)\n    return 'done'", "label": 1, "type": "insecure_eval"},

    # NEW: Flask request body passed to eval
    {"code": "def calculate_api(request):\n    expr = request.json.get('expression')\n    return eval(expr)", "label": 1, "type": "insecure_eval"},

    # NEW: eval inside loop on user-supplied list
    {"code": "def batch_eval(expressions):\n    results = []\n    for expr in expressions:\n        results.append(eval(expr))\n    return results", "label": 1, "type": "insecure_eval"},

    # NEW: class method using exec
    {"code": "class ScriptRunner:\n    def run(self, script):\n        exec(script)\n        return 'executed'", "label": 1, "type": "insecure_eval"},

    # NEW: exec with globals() — especially dangerous
    {"code": "def load_config(config_str):\n    exec(config_str, globals())\n    return 'loaded'", "label": 1, "type": "insecure_eval"},

    # ── SAFE (label=0) ────────────────────────────

    {"code": "def calculate(expr):\n    allowed = set('0123456789+-*/(). ')\n    if all(c in allowed for c in expr):\n        return eval(expr)\n    raise ValueError('Invalid expression')", "label": 0, "type": "safe"},

    {"code": "def compute(a, b, op):\n    ops = {'+': lambda x,y: x+y, '-': lambda x,y: x-y, '*': lambda x,y: x*y}\n    if op not in ops:\n        raise ValueError('Invalid operator')\n    return ops[op](a, b)", "label": 0, "type": "safe"},

    {"code": "def parse_value(val_str):\n    import ast\n    return ast.literal_eval(val_str)", "label": 0, "type": "safe"},

    {"code": "def evaluate_expr(expression):\n    import ast\n    tree = ast.parse(expression, mode='eval')\n    return ast.literal_eval(tree)", "label": 0, "type": "safe"},

    {"code": "def run_operation(op, a, b):\n    operations = {'add': a+b, 'sub': a-b, 'mul': a*b, 'div': a/b}\n    return operations.get(op)", "label": 0, "type": "safe"},

    {"code": "def process_formula(a, b, operator):\n    if operator == '+':\n        return a + b\n    elif operator == '-':\n        return a - b\n    raise ValueError('Unsupported operator')", "label": 0, "type": "safe"},

    {"code": "def apply_rule(rule_name, value):\n    rules = {'double': lambda v: v*2, 'square': lambda v: v**2, 'negate': lambda v: -v}\n    fn = rules.get(rule_name)\n    if not fn:\n        raise ValueError('Unknown rule')\n    return fn(value)", "label": 0, "type": "safe"},

    {"code": "def compute_metric(metric_name, data):\n    if metric_name == 'sum':\n        return sum(data)\n    if metric_name == 'avg':\n        return sum(data)/len(data)\n    raise ValueError('Unknown metric')", "label": 0, "type": "safe"},

    {"code": "def parse_condition(field, op, value):\n    if op == 'eq':\n        return field == value\n    if op == 'gt':\n        return field > value\n    return False", "label": 0, "type": "safe"},

    {"code": "def run_filter(filter_type, items):\n    filters = {'active': lambda x: x.active, 'recent': lambda x: x.recent}\n    fn = filters.get(filter_type)\n    return list(filter(fn, items)) if fn else items", "label": 0, "type": "safe"},

    {"code": "def evaluate_condition(condition_dict):\n    field = condition_dict.get('field')\n    value = condition_dict.get('value')\n    return field == value", "label": 0, "type": "safe"},

    {"code": "def apply_function(func_name, data):\n    allowed = {'upper': str.upper, 'lower': str.lower, 'strip': str.strip}\n    fn = allowed.get(func_name)\n    return fn(data) if fn else data", "label": 0, "type": "safe"},

    {"code": "def process_query(query_dict):\n    return {k: v for k, v in query_dict.items() if v is not None}", "label": 0, "type": "safe"},

    {"code": "def run_macro(macro_name, context):\n    macros = {'greet': lambda c: f'Hello {c[\"name\"]}', 'bye': lambda c: f'Bye {c[\"name\"]}'}\n    fn = macros.get(macro_name)\n    return fn(context) if fn else None", "label": 0, "type": "safe"},

    {"code": "def apply_transform(transform_name, value):\n    transforms = {'double': lambda v: v*2, 'triple': lambda v: v*3}\n    fn = transforms.get(transform_name)\n    return fn(value) if fn else value", "label": 0, "type": "safe"},

    {"code": "def dynamic_calc(operation, x, y):\n    import operator\n    ops = {'add': operator.add, 'sub': operator.sub, 'mul': operator.mul}\n    if operation not in ops:\n        raise ValueError('Unknown operation')\n    return ops[operation](x, y)", "label": 0, "type": "safe"},

    {"code": "def compute_value(formula_type, inputs):\n    if formula_type == 'sum':\n        return sum(inputs)\n    if formula_type == 'product':\n        result = 1\n        for i in inputs:\n            result *= i\n        return result\n    raise ValueError('Unknown formula')", "label": 0, "type": "safe"},

    {"code": "def run_validator(validator_name, value):\n    validators = {'email': lambda v: '@' in v, 'phone': lambda v: v.isdigit()}\n    fn = validators.get(validator_name)\n    return fn(value) if fn else False", "label": 0, "type": "safe"},

    {"code": "def parse_expression(expr_dict):\n    left = expr_dict.get('left')\n    right = expr_dict.get('right')\n    op = expr_dict.get('op')\n    if op == 'add':\n        return left + right\n    return None", "label": 0, "type": "safe"},

    {"code": "def execute_script(script_name):\n    allowed_scripts = ['cleanup', 'backup', 'report']\n    if script_name not in allowed_scripts:\n        raise ValueError('Script not allowed')\n    return subprocess.run([script_name])", "label": 0, "type": "safe"},

    # NEW: safe compile alternative — never run compile on user input
    {"code": "def run_dynamic(operation_name, value):\n    ops = {'double': lambda v: v*2, 'abs': abs, 'round': round}\n    fn = ops.get(operation_name)\n    if not fn:\n        raise ValueError('Unknown operation')\n    return fn(value)", "label": 0, "type": "safe"},

    # NEW: safe Flask request — parse as JSON not eval
    {"code": "def calculate_api(request):\n    data = request.json\n    a = float(data.get('a', 0))\n    b = float(data.get('b', 0))\n    op = data.get('op')\n    if op == 'add': return a + b\n    if op == 'mul': return a * b\n    raise ValueError('Invalid operation')", "label": 0, "type": "safe"},

    # NEW: safe batch — use ast.literal_eval for data parsing
    {"code": "def batch_eval(expressions):\n    import ast\n    results = []\n    for expr in expressions:\n        results.append(ast.literal_eval(expr))\n    return results", "label": 0, "type": "safe"},

    # NEW: safe class method
    {"code": "class ScriptRunner:\n    ALLOWED = ['cleanup', 'backup', 'lint']\n    def run(self, script_name):\n        if script_name not in self.ALLOWED:\n            raise ValueError('Script not allowed')\n        return subprocess.run([script_name])", "label": 0, "type": "safe"},

    # NEW: safe config loading — use json not exec
    {"code": "def load_config(config_str):\n    import json\n    config = json.loads(config_str)\n    return config", "label": 0, "type": "safe"},
]

script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'insecure_eval.json')
with open(save_path, 'w') as f:
    json.dump(insecure_eval, f, indent=2)

print(f"Saved: {save_path}")
print(f"Total:      {len(insecure_eval)}")
print(f"Vulnerable: {sum(1 for e in insecure_eval if e['label'] == 1)}")
print(f"Safe:       {sum(1 for e in insecure_eval if e['label'] == 0)}")
# %%