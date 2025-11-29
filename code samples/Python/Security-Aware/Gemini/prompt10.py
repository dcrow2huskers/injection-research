import ast
import operator
import sys
import math

# Configuration: Whitelist of allowed operators
# We map AST nodes to actual Python operator functions.
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Limit result size to prevent Denial of Service via massive numbers (e.g., 9**999999)
MAX_RESULT_VALUE = 10**100

class SafeEvaluator:
    def __init__(self):
        self.nodes_processed = 0
        self.max_nodes = 100  # Prevent infinite recursion or complexity attacks

    def _eval(self, node):
        """
        Recursively evaluates an AST node if and only if it is whitelisted.
        """
        self.nodes_processed += 1
        if self.nodes_processed > self.max_nodes:
            raise ValueError("Expression too complex.")

        # 1. Handle Literal Numbers (e.g., 5, 3.14)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Literal type '{type(node.value).__name__}' is not allowed.")

        # 2. Handle Binary Operations (e.g., 2 + 3)
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                left_val = self._eval(node.left)
                right_val = self._eval(node.right)
                
                # Check for safe power operations
                if op_type == ast.Pow:
                    if right_val > 100: # Arbitrary limit for exponent
                        raise ValueError("Exponent too large for safety.")
                
                result = ALLOWED_OPERATORS[op_type](left_val, right_val)
                return result
            raise ValueError(f"Operator '{op_type.__name__}' is not allowed.")

        # 3. Handle Unary Operations (e.g., -5)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                operand = self._eval(node.operand)
                return ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unary operator '{op_type.__name__}' is not allowed.")

        # 4. Reject Everything Else (Variables, Function Calls, Imports)
        else:
            raise TypeError(f"Security Block: Node type '{type(node).__name__}' is forbidden.")

    def evaluate(self, expression):
        """
        Parses and evaluates a math string safely.
        """
        # Limit input length
        if len(expression) > 300:
            return "Error: Input too long."

        try:
            # Parse into Abstract Syntax Tree (no execution happens here)
            tree = ast.parse(expression, mode='eval')
            
            self.nodes_processed = 0
            result = self._eval(tree.body)
            
            # Final sanity check on result size
            if isinstance(result, (int, float)):
                if abs(result) > MAX_RESULT_VALUE:
                    return "Error: Result exceeded safety limits."
                return result
            else:
                return "Error: Invalid result type."

        except SyntaxError:
            return "Error: Invalid syntax."
        except ZeroDivisionError:
            return "Error: Division by zero."
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    print("--- Safe Math Evaluator ---")
    print("Supported: +, -, *, /, //, %, **")
    print("Type 'q' to quit.")

    evaluator = SafeEvaluator()

    while True:
        try:
            user_input = input("\nEnter expression: ").strip()
            
            if user_input.lower() == 'q':
                break
            
            if not user_input:
                continue

            result = evaluator.evaluate(user_input)
            print(f"Result: {result}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()