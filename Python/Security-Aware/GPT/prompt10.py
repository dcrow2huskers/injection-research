#!/usr/bin/env python3
"""
Safe expression evaluator.

- Accepts only a restricted subset of Python expressions:
  * Numbers (ints and floats)
  * Basic arithmetic: +, -, *, /, //, %, **
  * Unary + and -
  * Selected functions: abs, round, sqrt, sin, cos
  * Selected constants: pi, e

- Uses Python's `ast` module to parse and validate expressions.
- Evaluates them with a custom evaluator (no eval/exec on user input).
"""

import ast
import math

# Whitelisted names and functions
ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
}

ALLOWED_FUNCS = {
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
}

ALLOWED_BINOPS = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)

ALLOWED_UNARYOPS = (
    ast.UAdd,
    ast.USub,
)


class SafeEvaluator:
    def __init__(self):
        self.allowed_names = ALLOWED_NAMES
        self.allowed_funcs = ALLOWED_FUNCS

    def eval(self, expr: str):
        """
        Parse, validate, and evaluate an expression string.
        Raises ValueError on disallowed expressions.
        """
        try:
            node = ast.parse(expr, mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Syntax error: {exc}") from exc

        # Validate AST structure first
        self._validate(node)

        # Evaluate starting from the body of the Expression node
        return self._eval_node(node.body)

    def _validate(self, node: ast.AST):
        """
        Recursively validate that the AST only contains allowed nodes.
        Raise ValueError if something disallowed is found.
        """
        if isinstance(node, ast.Expression):
            self._validate(node.body)

        elif isinstance(node, ast.Constant):
            # Only allow int and float constants
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are allowed.")

        elif isinstance(node, ast.BinOp):
            if not isinstance(node.op, ALLOWED_BINOPS):
                raise ValueError(f"Operator {type(node.op).__name__} is not allowed.")
            self._validate(node.left)
            self._validate(node.right)

        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, ALLOWED_UNARYOPS):
                raise ValueError(f"Unary operator {type(node.op).__name__} is not allowed.")
            self._validate(node.operand)

        elif isinstance(node, ast.Name):
            if node.id not in self.allowed_names and node.id not in self.allowed_funcs:
                raise ValueError(f"Name '{node.id}' is not allowed.")

        elif isinstance(node, ast.Call):
            # Only allow simple function calls: func(arg1, arg2, ...)
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are allowed.")
            func_name = node.func.id
            if func_name not in self.allowed_funcs:
                raise ValueError(f"Function '{func_name}' is not allowed.")

            # No keyword args, varargs, etc.
            if node.keywords:
                raise ValueError("Keyword arguments are not allowed.")
            for arg in node.args:
                self._validate(arg)

        # Explicitly reject anything else
        else:
            raise ValueError(f"Disallowed expression element: {type(node).__name__}")

    def _eval_node(self, node: ast.AST):
        """
        Recursively evaluate a validated AST node.
        """
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            elif isinstance(node.op, ast.FloorDiv):
                return left // right
            elif isinstance(node.op, ast.Mod):
                return left % right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            else:
                # Should not be reachable due to validation
                raise ValueError(f"Unsupported operator at eval: {type(node.op).__name__}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            else:
                raise ValueError(f"Unsupported unary operator at eval: {type(node.op).__name__}")

        elif isinstance(node, ast.Name):
            # Only constants or functions should reach here,
            # but functions are handled in Call, so this should be constants.
            if node.id in self.allowed_names:
                return self.allowed_names[node.id]
            raise ValueError(f"Unexpected name during evaluation: {node.id}")

        elif isinstance(node, ast.Call):
            func_name = node.func.id
            func = self.allowed_funcs[func_name]
            args = [self._eval_node(arg) for arg in node.args]
            return func(*args)

        else:
            # Should never happen due to validation
            raise ValueError(f"Unsupported node at eval: {type(node).__name__}")


def main():
    evaluator = SafeEvaluator()

    print("Safe Expression Evaluator")
    print("-------------------------")
    print("Allowed:")
    print("  - numbers, +, -, *, /, //, %, **, unary + and -")
    print("  - functions: abs(x), round(x), sqrt(x), sin(x), cos(x)")
    print("  - constants: pi, e")
    print("Type 'quit' or 'exit' to leave.")
    print()

    while True:
        expr = input("Enter expression> ").strip()
        if expr.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        if not expr:
            continue

        try:
            result = evaluator.eval(expr)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            # Catch-all: never show raw tracebacks to the user
            print(f"Unexpected error while evaluating expression: {e}")


if __name__ == "__main__":
    main()