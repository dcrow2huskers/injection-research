import math
import operator

def evaluate_expression(expression):
    """
    Evaluate a mathematical expression and return the result.
    
    Args:
        expression: String containing the expression to evaluate
    
    Returns:
        The result of the evaluation
    """
    try:
        # Use eval() to evaluate the expression
        result = eval(expression)
        return result
    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError:
        return "Error: Invalid syntax in expression"
    except NameError as e:
        return f"Error: Unknown variable or function - {e}"
    except TypeError as e:
        return f"Error: Type error - {e}"
    except Exception as e:
        return f"Error: {type(e).__name__} - {e}"

def show_help():
    """Display help information about available operations"""
    print("\n" + "="*70)
    print("EXPRESSION EVALUATOR - HELP")
    print("="*70)
    print("\nBasic Operations:")
    print("  +  Addition        : 5 + 3")
    print("  -  Subtraction     : 10 - 4")
    print("  *  Multiplication  : 6 * 7")
    print("  /  Division        : 15 / 3")
    print("  // Floor Division  : 17 // 5")
    print("  %  Modulo          : 17 % 5")
    print("  ** Power           : 2 ** 8")
    
    print("\nMath Functions (from math module):")
    print("  sqrt(x)    : Square root      - sqrt(16)")
    print("  pow(x,y)   : Power            - pow(2, 3)")
    print("  sin(x)     : Sine             - sin(math.pi/2)")
    print("  cos(x)     : Cosine           - cos(0)")
    print("  tan(x)     : Tangent          - tan(math.pi/4)")
    print("  log(x)     : Natural log      - log(10)")
    print("  log10(x)   : Base-10 log      - log10(100)")
    print("  exp(x)     : e^x              - exp(1)")
    print("  floor(x)   : Floor            - floor(3.7)")
    print("  ceil(x)    : Ceiling          - ceil(3.2)")
    print("  abs(x)     : Absolute value   - abs(-5)")
    
    print("\nConstants:")
    print("  math.pi    : π (3.14159...)")
    print("  math.e     : e (2.71828...)")
    
    print("\nComplex Expressions:")
    print("  (5 + 3) * 2")
    print("  2 ** (3 + 4)")
    print("  sqrt(16) + pow(2, 3)")
    print("  sin(math.pi/6) * 2")
    
    print("\nComparisons (return True/False):")
    print("  5 > 3")
    print("  10 == 10")
    print("  7 <= 8")
    
    print("="*70)

def show_examples():
    """Display example expressions"""
    print("\n" + "="*70)
    print("EXAMPLE EXPRESSIONS")
    print("="*70)
    examples = [
        ("2 + 2", "Basic addition"),
        ("10 * 5 - 3", "Order of operations"),
        ("(5 + 3) * 2", "Using parentheses"),
        ("2 ** 10", "Powers (2 to the 10th)"),
        ("sqrt(144)", "Square root"),
        ("math.pi * 2", "Using constants"),
        ("sin(math.pi/2)", "Trigonometry"),
        ("log10(1000)", "Logarithm base 10"),
        ("abs(-42)", "Absolute value"),
        ("17 % 5", "Modulo (remainder)"),
    ]
    
    for expr, desc in examples:
        result = evaluate_expression(expr)
        print(f"\n  {expr:<25} → {result:<15} ({desc})")
    
    print("="*70)

def main():
    """Main function to run the expression evaluator"""
    print("="*70)
    print("           PYTHON EXPRESSION EVALUATOR")
    print("="*70)
    print("\nEnter mathematical expressions to evaluate.")
    print("Type 'help' for available functions and operators")
    print("Type 'examples' to see example expressions")
    print("Type 'quit' to exit")
    
    while True:
        print("\n" + "-"*70)
        
        # Prompt user for expression
        expression = input("\nEnter expression: ").strip()
        
        # Check for exit command
        if expression.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        # Check for help command
        if expression.lower() == 'help':
            show_help()
            continue
        
        # Check for examples command
        if expression.lower() == 'examples':
            show_examples()
            continue
        
        # Check for empty input
        if not expression:
            print("Please enter an expression")
            continue
        
        # Evaluate the expression
        print(f"\nExpression: {expression}")
        result = evaluate_expression(expression)
        print(f"Result: {result}")
        
        # Show type of result if it's a number
        if isinstance(result, (int, float, complex)):
            print(f"Type: {type(result).__name__}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")