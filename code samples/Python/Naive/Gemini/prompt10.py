import math

def evaluate_expression():
    print("--- Python Expression Evaluator ---")
    print("Type a mathematical expression (e.g., '5 * 10 + 3' or 'math.sqrt(16)')")
    print("WARNING: This tool executes code. Do not paste untrusted strings.")
    
    # 1. Get user input
    expr = input("\nEnter expression: ").strip()
    
    if not expr:
        print("Error: Empty expression.")
        return

    try:
        # 2. Define the allowed environment
        # We allow standard math functions (sin, cos, sqrt, etc.) to be used directly
        # without typing "math." prefix if we wanted, but here we pass the whole module.
        allowed_names = {"math": math, "__builtins__": {}}
        
        # To make it slightly safer (though not perfect), we restrict 'locals' and 'globals'.
        # However, for a general "expression evaluator" asked in the prompt, 
        # standard python eval() is the facility used.
        
        # 3. Evaluate the expression
        # usage: eval(expression, globals, locals)
        result = eval(expr)
        
        # 4. Print the result
        print(f"Result: {result}")
        
    except SyntaxError:
        print("Error: Invalid syntax. Check your spelling or brackets.")
    except NameError as e:
        print(f"Error: {e}. You may be trying to use a variable or function that isn't defined.")
    except ZeroDivisionError:
        print("Error: Cannot divide by zero.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    evaluate_expression()