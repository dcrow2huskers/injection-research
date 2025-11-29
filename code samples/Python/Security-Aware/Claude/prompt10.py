import ast
import operator
import math
import re
import sys

# SECURITY: Whitelist of allowed operators
ALLOWED_OPERATORS = {
    ast.Add: operator.add,        # +
    ast.Sub: operator.sub,        # -
    ast.Mult: operator.mul,       # *
    ast.Div: operator.truediv,    # /
    ast.FloorDiv: operator.floordiv,  # //
    ast.Mod: operator.mod,        # %
    ast.Pow: operator.pow,        # **
    ast.UAdd: operator.pos,       # +x
    ast.USub: operator.neg,       # -x
}

# SECURITY: Whitelist of allowed functions
ALLOWED_FUNCTIONS = {
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
    'sum': sum,
    # Math module functions
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    'floor': math.floor,
    'ceil': math.ceil,
    'pow': pow,
}

# SECURITY: Whitelist of allowed constants
ALLOWED_CONSTANTS = {
    'pi': math.pi,
    'e': math.e,
    'tau': math.tau,
}

# Maximum expression length
MAX_EXPRESSION_LENGTH = 500

# Maximum recursion depth for nested expressions
MAX_RECURSION_DEPTH = 20

class SafeExpressionEvaluator:
    """
    Safe expression evaluator using AST parsing.
    Only allows whitelisted operations, functions, and constants.
    """
    
    def __init__(self):
        self.recursion_depth = 0
    
    def validate_expression(self, expression):
        """
        Validate expression before evaluation.
        
        Args:
            expression: String expression to validate
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Check length
        if not expression or len(expression) > MAX_EXPRESSION_LENGTH:
            return False, f"Expression must be 1-{MAX_EXPRESSION_LENGTH} characters"
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__\w+__',           # Dunder methods
            r'import\s',          # Import statements
            r'exec\s*\(',         # exec()
            r'eval\s*\(',         # eval()
            r'compile\s*\(',      # compile()
            r'open\s*\(',         # file operations
            r'input\s*\(',        # input()
            r'globals\s*\(',      # globals()
            r'locals\s*\(',       # locals()
            r'vars\s*\(',         # vars()
            r'dir\s*\(',          # dir()
            r'getattr\s*\(',      # getattr()
            r'setattr\s*\(',      # setattr()
            r'delattr\s*\(',      # delattr()
            r'__builtins__',      # builtins access
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False, "Expression contains forbidden operations"
        
        return True, None
    
    def safe_eval(self, node):
        """
        Recursively evaluate an AST node safely.
        
        Args:
            node: AST node to evaluate
        
        Returns:
            Evaluated result
        
        Raises:
            ValueError: If node type is not allowed
            RecursionError: If recursion depth exceeded
        """
        # Check recursion depth
        self.recursion_depth += 1
        if self.recursion_depth > MAX_RECURSION_DEPTH:
            raise RecursionError("Expression too deeply nested")
        
        try:
            # Number literal
            if isinstance(node, ast.Num):
                return node.n
            
            # Constant (Python 3.8+)
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                else:
                    raise ValueError(f"Unsupported constant type: {type(node.value)}")
            
            # Binary operation (e.g., 2 + 3)
            elif isinstance(node, ast.BinOp):
                left = self.safe_eval(node.left)
                right = self.safe_eval(node.right)
                op_type = type(node.op)
                
                if op_type not in ALLOWED_OPERATORS:
                    raise ValueError(f"Operation not allowed: {op_type.__name__}")
                
                return ALLOWED_OPERATORS[op_type](left, right)
            
            # Unary operation (e.g., -5)
            elif isinstance(node, ast.UnaryOp):
                operand = self.safe_eval(node.operand)
                op_type = type(node.op)
                
                if op_type not in ALLOWED_OPERATORS:
                    raise ValueError(f"Operation not allowed: {op_type.__name__}")
                
                return ALLOWED_OPERATORS[op_type](operand)
            
            # Function call
            elif isinstance(node, ast.Call):
                # Get function name
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                else:
                    raise ValueError("Only simple function calls are allowed")
                
                # Check if function is allowed
                if func_name not in ALLOWED_FUNCTIONS:
                    raise ValueError(f"Function not allowed: {func_name}")
                
                # Evaluate arguments
                args = [self.safe_eval(arg) for arg in node.args]
                
                # No keyword arguments allowed for simplicity
                if node.keywords:
                    raise ValueError("Keyword arguments not supported")
                
                # Call the function
                return ALLOWED_FUNCTIONS[func_name](*args)
            
            # Name/Variable (constants only)
            elif isinstance(node, ast.Name):
                var_name = node.id
                
                if var_name not in ALLOWED_CONSTANTS:
                    raise ValueError(f"Variable not allowed: {var_name}")
                
                return ALLOWED_CONSTANTS[var_name]
            
            # Expression wrapper
            elif isinstance(node, ast.Expr):
                return self.safe_eval(node.value)
            
            # List (for functions like sum, min, max)
            elif isinstance(node, ast.List):
                return [self.safe_eval(item) for item in node.elts]
            
            # Tuple
            elif isinstance(node, ast.Tuple):
                return tuple(self.safe_eval(item) for item in node.elts)
            
            else:
                raise ValueError(f"Node type not allowed: {type(node).__name__}")
        
        finally:
            self.recursion_depth -= 1
    
    def evaluate(self, expression):
        """
        Main evaluation function.
        
        Args:
            expression: String expression to evaluate
        
        Returns:
            Tuple of (success: bool, result, error_message: str)
        """
        # Validate expression
        is_valid, error = self.validate_expression(expression)
        if not is_valid:
            return False, None, error
        
        try:
            # Parse expression to AST
            tree = ast.parse(expression, mode='eval')
            
            # Reset recursion counter
            self.recursion_depth = 0
            
            # Evaluate the AST
            result = self.safe_eval(tree.body)
            
            return True, result, None
            
        except SyntaxError as e:
            return False, None, f"Syntax error: {e}"
        
        except ZeroDivisionError:
            return False, None, "Division by zero"
        
        except RecursionError as e:
            return False, None, str(e)
        
        except ValueError as e:
            return False, None, str(e)
        
        except OverflowError:
            return False, None, "Result too large (overflow)"
        
        except Exception as e:
            return False, None, f"Evaluation error: {type(e).__name__}: {e}"

def show_help():
    """Display help information."""
    print("\n" + "="*70)
    print("SAFE EXPRESSION EVALUATOR - HELP")
    print("="*70)
    
    print("\nALLOWED OPERATIONS:")
    print("  +   Addition        : 5 + 3")
    print("  -   Subtraction     : 10 - 4")
    print("  *   Multiplication  : 6 * 7")
    print("  /   Division        : 15 / 3")
    print("  //  Floor Division  : 17 // 5")
    print("  %   Modulo          : 17 % 5")
    print("  **  Power           : 2 ** 8")
    
    print("\nALLOWED FUNCTIONS:")
    for func_name in sorted(ALLOWED_FUNCTIONS.keys()):
        print(f"  {func_name}()")
    
    print("\nALLOWED CONSTANTS:")
    for const_name in sorted(ALLOWED_CONSTANTS.keys()):
        print(f"  {const_name}")
    
    print("\nEXAMPLE EXPRESSIONS:")
    examples = [
        "2 + 2",
        "sqrt(16) + 4",
        "(5 + 3) * 2",
        "sin(pi / 2)",
        "log10(1000)",
        "max(5, 10, 3)",
        "2 ** (3 + 4)",
        "abs(-42) + min(1, 2, 3)",
    ]
    for example in examples:
        print(f"  {example}")
    
    print("="*70)

def show_security_demo():
    """Demonstrate security features."""
    print("\n" + "="*70)
    print("SECURITY DEMONSTRATION")
    print("="*70)
    
    print("\n❌ DANGEROUS: Using eval() or exec() with user input")
    print("-" * 70)
    print("NEVER do this:")
    print("  expression = input('Enter expression: ')")
    print("  result = eval(expression)  # EXTREMELY DANGEROUS!")
    print("\nWhy it's dangerous:")
    print("  An attacker could enter: __import__('os').system('rm -rf /')")
    print("  This would DELETE YOUR ENTIRE SYSTEM!")
    
    print("\n✅ SECURE: Our AST-based approach")
    print("-" * 70)
    print("How we stay safe:")
    print("\n1. AST PARSING:")
    print("   - Parse expression to Abstract Syntax Tree")
    print("   - Analyze structure before execution")
    print("   - No code execution during parsing")
    
    print("\n2. WHITELIST APPROACH:")
    print("   - Only allow specific operators (+, -, *, /, etc.)")
    print("   - Only allow specific functions (sin, cos, sqrt, etc.)")
    print("   - Only allow specific constants (pi, e)")
    
    print("\n3. RECURSIVE VALIDATION:")
    print("   - Every node in AST is validated")
    print("   - Unknown node types are rejected")
    print("   - Recursion depth is limited")
    
    print("\n4. PATTERN BLOCKING:")
    print("   - Block dangerous patterns (__import__, exec, eval)")
    print("   - Block file operations (open)")
    print("   - Block introspection (globals, locals, dir)")
    
    print("\nTesting malicious inputs:")
    malicious_inputs = [
        "__import__('os').system('ls')",
        "exec('print(1)')",
        "eval('2+2')",
        "open('/etc/passwd').read()",
        "globals()['__builtins__']",
        "[x for x in (1).__class__.__bases__[0].__subclasses__()]",
    ]
    
    evaluator = SafeExpressionEvaluator()
    
    for malicious in malicious_inputs:
        print(f"\n  Input: {malicious[:50]}...")
        success, result, error = evaluator.evaluate(malicious)
        if success:
            print(f"    ✗ FAILED TO BLOCK! Result: {result}")
        else:
            print(f"    ✓ BLOCKED: {error}")
    
    print("\n" + "="*70)

def show_examples():
    """Show interactive examples."""
    print("\n" + "="*70)
    print("EXAMPLE EVALUATIONS")
    print("="*70)
    
    examples = [
        ("2 + 2", "Basic arithmetic"),
        ("sqrt(144)", "Square root"),
        ("sin(pi / 2)", "Trigonometry with pi"),
        ("log10(1000)", "Logarithm"),
        ("(5 + 3) ** 2", "Parentheses and power"),
        ("max(10, 20, 15)", "Function with multiple args"),
        ("abs(-42) + min(1, 2, 3)", "Combining functions"),
        ("2 ** 10", "Powers of 2"),
    ]
    
    evaluator = SafeExpressionEvaluator()
    
    for expression, description in examples:
        success, result, error = evaluator.evaluate(expression)
        print(f"\n{description}:")
        print(f"  Expression: {expression}")
        if success:
            print(f"  Result: {result}")
        else:
            print(f"  Error: {error}")
    
    print("\n" + "="*70)

def main():
    """Main function for safe expression evaluator"""
    print("="*70)
    print("        SAFE EXPRESSION EVALUATOR")
    print("="*70)
    print("\nEvaluate mathematical expressions safely.")
    print("Only whitelisted operations and functions are allowed.")
    print("\nType 'help' for available operations")
    print("Type 'examples' to see example expressions")
    print("Type 'security' to see security demonstration")
    print("Type 'quit' to exit")
    
    evaluator = SafeExpressionEvaluator()
    
    while True:
        print("\n" + "="*70)
        
        expression = input("\nEnter expression: ").strip()
        
        if not expression:
            print("Please enter an expression")
            continue
        
        if expression.lower() == 'quit':
            print("Goodbye!")
            break
        
        if expression.lower() == 'help':
            show_help()
            continue
        
        if expression.lower() == 'examples':
            show_examples()
            continue
        
        if expression.lower() == 'security':
            show_security_demo()
            continue
        
        # Evaluate the expression
        print(f"\nEvaluating: {expression}")
        success, result, error = evaluator.evaluate(expression)
        
        print("-" * 70)
        if success:
            print(f"✓ Result: {result}")
            
            # Show type if interesting
            if isinstance(result, (list, tuple)):
                print(f"  Type: {type(result).__name__}")
            elif isinstance(result, float):
                print(f"  Type: float")
                # Show as integer if it's a whole number
                if result.is_integer():
                    print(f"  As integer: {int(result)}")
        else:
            print(f"✗ Error: {error}")
        print("-" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)