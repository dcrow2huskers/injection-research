import ast
import operator as op

# Allowed operators
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def eval_expr(expr):
    """
    Safely evaluate a mathematical expression using AST.
    """
    def _eval(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            if type(node.op) not in operators:
                raise ValueError("Unsupported operator")
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):  # - <operand>
            if type(node.op) not in operators:
                raise ValueError("Unsupported unary operator")
            return operators[type(node.op)](_eval(node.operand))
        else:
            raise ValueError("Unsupported expression type")

    tree = ast.parse(expr, mode='eval')
    return _eval(tree.body)

def main():
    expr = input("Enter an expression to evaluate: ")
    try:
        result = eval_expr(expr)
        print("Result:", result)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()