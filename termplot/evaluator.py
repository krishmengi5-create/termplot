import math
import re

SAFE_METHODS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'atan2': math.atan2,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'exp': math.exp,
    'log': math.log,
    'log10': math.log10,
    'sqrt': math.sqrt,
    'abs': abs,
    'pow': pow,
    'pi': math.pi,
    'e': math.e,
    'ceil': math.ceil,
    'floor': math.floor,
}

def preprocess_expression(expr):
    # Remove whitespace
    expr = expr.strip()
    # Replace ^ with **
    expr = expr.replace('^', '**')
    # Replace implicit multiplication like 2x with 2*x
    expr = re.sub(r'(\d+)([a-zA-Z\(])', r'\1*\2', expr)
    # Replace implicit multiplication between closing parenthesis and opening parenthesis / variables
    expr = re.sub(r'\)\(', r')*(', expr)
    expr = re.sub(r'\)([a-zA-Z0-9])', r')*\1', expr)
    return expr

def safe_eval(expr, x_val):
    expr_processed = preprocess_expression(expr)
    local_dict = {**SAFE_METHODS, 'x': x_val}
    try:
        val = eval(expr_processed, {"__builtins__": None}, local_dict)
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return None
            return float(val)
        return None
    except Exception:
        return None
