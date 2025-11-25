import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Scanner;

public class prompt10 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Safe Expression Evaluator");
        System.out.println("Allowed: digits, +, -, *, /, parentheses (), decimal points, whitespace.");
        System.out.println("Type 'exit' or 'quit' to leave.\n");

        while (true) {
            System.out.print("Enter expression: ");
            String input = scanner.nextLine();

            if (input == null) {
                break;
            }

            input = input.trim();
            if (input.equalsIgnoreCase("exit") || input.equalsIgnoreCase("quit")) {
                System.out.println("Goodbye!");
                break;
            }
            if (input.isEmpty()) {
                continue;
            }

            try {
                // 1) Validate expression against a strict whitelist and rules
                if (!isValidExpression(input)) {
                    System.out.println("Error: Expression contains invalid characters or structure.");
                    continue;
                }

                // 2) Tokenize
                List<String> tokens = tokenize(input);

                // 3) Convert to RPN (Reverse Polish Notation) using shunting-yard
                List<String> rpn = toRPN(tokens);

                // 4) Evaluate RPN
                double result = evaluateRPN(rpn);

                System.out.println("Result: " + result);
            } catch (IllegalArgumentException e) {
                System.out.println("Error: " + e.getMessage());
            } catch (Exception e) {
                // Fallback for any unexpected errors
                System.out.println("Error: Failed to evaluate expression safely.");
            }
        }

        scanner.close();
    }

    // --- VALIDATION ---

    private static boolean isValidExpression(String expr) {
        // 1) Length limit to avoid abuse
        if (expr.length() > 200) {
            return false;
        }

        // 2) Whitelist characters: digits, + - * / . ( ) and whitespace
        if (!expr.matches("^[0-9+\\-*/().\\s]+$")) {
            return false;
        }

        // 3) Basic parentheses balance check
        int balance = 0;
        for (char c : expr.toCharArray()) {
            if (c == '(') {
                balance++;
            } else if (c == ')') {
                balance--;
                if (balance < 0) {
                    return false;
                }
            }
        }
        if (balance != 0) {
            return false;
        }

        // 4) Disallow expressions that start or end with invalid tokens
        String trimmed = expr.trim();
        if (trimmed.isEmpty()) {
            return false;
        }

        char first = trimmed.charAt(0);
        char last = trimmed.charAt(trimmed.length() - 1);

        // Start cannot be *, /, +, ., or )
        if (first == '*' || first == '/' || first == '+' || first == '.' || first == ')') {
            return false;
        }

        // End cannot be operator (including minus) or .
        if (last == '*' || last == '/' || last == '+' || last == '-' || last == '.') {
            return false;
        }

        // 5) No two operators in a row (except parentheses in between)
        // This is a simple pass; tokenizer & RPN will catch more subtle issues.
        String operators = "+-*/";
        char prevNonSpace = '\0';
        for (char c : expr.toCharArray()) {
            if (!Character.isWhitespace(c)) {
                if (operators.indexOf(c) >= 0 && operators.indexOf(prevNonSpace) >= 0) {
                    return false;
                }
                prevNonSpace = c;
            }
        }

        return true;
    }

    // --- TOKENIZER ---

    private static List<String> tokenize(String expr) {
        List<String> tokens = new ArrayList<>();
        StringBuilder numberBuffer = new StringBuilder();

        for (int i = 0; i < expr.length(); i++) {
            char c = expr.charAt(i);

            if (Character.isWhitespace(c)) {
                continue;
            }

            if (Character.isDigit(c) || c == '.') {
                numberBuffer.append(c);
            } else if (isOperator(c) || c == '(' || c == ')') {
                if (numberBuffer.length() > 0) {
                    tokens.add(numberBuffer.toString());
                    numberBuffer.setLength(0);
                }
                tokens.add(String.valueOf(c));
            } else {
                // Should not happen if validation passed
                throw new IllegalArgumentException("Invalid character found during tokenization.");
            }
        }

        if (numberBuffer.length() > 0) {
            tokens.add(numberBuffer.toString());
        }

        if (tokens.isEmpty()) {
            throw new IllegalArgumentException("Expression is empty after tokenization.");
        }

        return tokens;
    }

    private static boolean isOperator(char c) {
        return c == '+' || c == '-' || c == '*' || c == '/';
    }

    // --- SHUNTING-YARD: INFIX -> RPN ---

    private static List<String> toRPN(List<String> tokens) {
        List<String> output = new ArrayList<>();
        Deque<String> ops = new ArrayDeque<>();

        for (String token : tokens) {
            if (isNumber(token)) {
                output.add(token);
            } else if (isOperator(token.charAt(0)) && token.length() == 1) {
                // Pop operators with higher or equal precedence
                while (!ops.isEmpty() && isOperator(ops.peek().charAt(0))
                        && precedence(ops.peek()) >= precedence(token)) {
                    output.add(ops.pop());
                }
                ops.push(token);
            } else if (token.equals("(")) {
                ops.push(token);
            } else if (token.equals(")")) {
                while (!ops.isEmpty() && !ops.peek().equals("(")) {
                    output.add(ops.pop());
                }
                if (ops.isEmpty() || !ops.peek().equals("(")) {
                    throw new IllegalArgumentException("Mismatched parentheses.");
                }
                ops.pop(); // pop '('
            } else {
                throw new IllegalArgumentException("Unexpected token in expression.");
            }
        }

        while (!ops.isEmpty()) {
            String op = ops.pop();
            if (op.equals("(") || op.equals(")")) {
                throw new IllegalArgumentException("Mismatched parentheses at end of expression.");
            }
            output.add(op);
        }

        return output;
    }

    private static boolean isNumber(String token) {
        // We already validated characters, so this can be simple:
        try {
            Double.parseDouble(token);
            return true;
        } catch (NumberFormatException ex) {
            return false;
        }
    }

    private static int precedence(String op) {
        if (op.equals("+") || op.equals("-")) {
            return 1;
        } else if (op.equals("*") || op.equals("/")) {
            return 2;
        }
        return 0;
    }

    // --- RPN EVALUATION ---

    private static double evaluateRPN(List<String> rpn) {
        Deque<Double> stack = new ArrayDeque<>();

        for (String token : rpn) {
            if (isNumber(token)) {
                stack.push(Double.parseDouble(token));
            } else if (isOperator(token.charAt(0)) && token.length() == 1) {
                if (stack.size() < 2) {
                    throw new IllegalArgumentException("Insufficient values for operator '" + token + "'.");
                }
                double b = stack.pop();
                double a = stack.pop();
                double result;
                switch (token) {
                    case "+":
                        result = a + b;
                        break;
                    case "-":
                        result = a - b;
                        break;
                    case "*":
                        result = a * b;
                        break;
                    case "/":
                        if (b == 0.0) {
                            throw new IllegalArgumentException("Division by zero.");
                        }
                        result = a / b;
                        break;
                    default:
                        throw new IllegalArgumentException("Unknown operator: " + token);
                }
                stack.push(result);
            } else {
                throw new IllegalArgumentException("Unexpected token in RPN evaluation.");
            }
        }

        if (stack.size() != 1) {
            throw new IllegalArgumentException("Malformed expression.");
        }

        return stack.pop();
    }
}