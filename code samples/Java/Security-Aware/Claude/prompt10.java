import java.util.*;
import java.util.regex.Pattern;

public class prompt10 {
    
    // Whitelist of allowed operators
    private static final Set<Character> ALLOWED_OPERATORS = new HashSet<>(
        Arrays.asList('+', '-', '*', '/', '%', '(', ')', '^')
    );
    
    // Whitelist of allowed functions
    private static final Set<String> ALLOWED_FUNCTIONS = new HashSet<>(
        Arrays.asList("sqrt", "abs", "sin", "cos", "tan", "log", "ln", "exp", "ceil", "floor", "round")
    );
    
    // Maximum expression length to prevent DoS
    private static final int MAX_EXPRESSION_LENGTH = 500;
    
    // Maximum recursion depth for evaluation
    private static final int MAX_DEPTH = 100;
    
    private int currentDepth = 0;
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Safe Expression Evaluator ===");
        System.out.println("Allowed operations: +, -, *, /, %, ^ (power), ( )");
        System.out.println("Allowed functions: sqrt, abs, sin, cos, tan, log, ln, exp, ceil, floor, round");
        System.out.println("Numbers: integers and decimals (e.g., 3.14, -5, 42)");
        System.out.println("Constants: pi, e");
        System.out.println("\nExamples:");
        System.out.println("  2 + 3 * 4");
        System.out.println("  sqrt(16) + abs(-5)");
        System.out.println("  (10 + 5) * 2 - 3");
        System.out.println("  sin(pi / 2)");
        System.out.println();
        
        while (true) {
            System.out.print("Enter expression (or 'quit' to exit): ");
            String input = scanner.nextLine().trim();
            
            if (input.equalsIgnoreCase("quit") || input.equalsIgnoreCase("exit")) {
                System.out.println("Exiting...");
                break;
            }
            
            if (input.isEmpty()) {
                System.out.println("Error: Expression cannot be empty.\n");
                continue;
            }
            
            try {
                SafeExpressionEvaluator evaluator = new SafeExpressionEvaluator();
                double result = evaluator.evaluate(input);
                
                // Format result nicely
                if (result == Math.floor(result) && !Double.isInfinite(result)) {
                    System.out.println("Result: " + (long)result);
                } else {
                    System.out.println("Result: " + result);
                }
                
            } catch (SecurityException e) {
                System.err.println("Security Error: " + e.getMessage());
            } catch (IllegalArgumentException e) {
                System.err.println("Invalid Expression: " + e.getMessage());
            } catch (ArithmeticException e) {
                System.err.println("Math Error: " + e.getMessage());
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
            
            System.out.println();
        }
        
        scanner.close();
    }
    
    /**
     * Main evaluation method with security checks
     */
    public double evaluate(String expression) {
        // Security check 1: Length validation
        if (expression.length() > MAX_EXPRESSION_LENGTH) {
            throw new SecurityException(
                "Expression too long (max " + MAX_EXPRESSION_LENGTH + " characters)"
            );
        }
        
        // Security check 2: Character validation
        if (!isExpressionSafe(expression)) {
            throw new SecurityException(
                "Expression contains invalid characters. Only numbers, operators, " +
                "parentheses, and whitelisted functions are allowed."
            );
        }
        
        // Security check 3: Check for suspicious patterns
        if (containsSuspiciousPatterns(expression)) {
            throw new SecurityException(
                "Expression contains suspicious patterns and has been rejected."
            );
        }
        
        // Replace constants
        expression = expression.replaceAll("\\bpi\\b", String.valueOf(Math.PI));
        expression = expression.replaceAll("\\be\\b", String.valueOf(Math.E));
        
        // Parse and evaluate
        currentDepth = 0;
        ExpressionParser parser = new ExpressionParser(expression);
        return parser.parse();
    }
    
    /**
     * Validates that expression only contains safe characters
     */
    private boolean isExpressionSafe(String expression) {
        for (char c : expression.toCharArray()) {
            if (!Character.isDigit(c) && 
                !Character.isWhitespace(c) && 
                !Character.isLetter(c) &&
                !ALLOWED_OPERATORS.contains(c) &&
                c != '.') {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Checks for code injection patterns and malicious content
     */
    private boolean containsSuspiciousPatterns(String expression) {
        String lower = expression.toLowerCase();
        
        // Block common code execution patterns
        String[] dangerousPatterns = {
            "exec", "eval", "runtime", "process", "system",
            "class", "reflect", "invoke", "script", "import",
            "while", "for", "if", "__", "$$"
        };
        
        for (String pattern : dangerousPatterns) {
            if (lower.contains(pattern)) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Inner class for parsing expressions using recursive descent parser
     */
    private class ExpressionParser {
        private String expression;
        private int pos = 0;
        private char currentChar;
        
        public ExpressionParser(String expression) {
            this.expression = expression.replaceAll("\\s+", ""); // Remove whitespace
            this.currentChar = expression.isEmpty() ? '\0' : expression.charAt(0);
        }
        
        private void advance() {
            pos++;
            currentChar = (pos < expression.length()) ? expression.charAt(pos) : '\0';
        }
        
        private void skipWhitespace() {
            while (currentChar == ' ' || currentChar == '\t') {
                advance();
            }
        }
        
        public double parse() {
            double result = parseExpression();
            if (currentChar != '\0') {
                throw new IllegalArgumentException("Unexpected character: " + currentChar);
            }
            return result;
        }
        
        // Parse addition and subtraction (lowest precedence)
        private double parseExpression() {
            checkDepth();
            double result = parseTerm();
            
            while (currentChar == '+' || currentChar == '-') {
                char op = currentChar;
                advance();
                double right = parseTerm();
                
                if (op == '+') {
                    result += right;
                } else {
                    result -= right;
                }
            }
            
            return result;
        }
        
        // Parse multiplication, division, and modulo
        private double parseTerm() {
            checkDepth();
            double result = parsePower();
            
            while (currentChar == '*' || currentChar == '/' || currentChar == '%') {
                char op = currentChar;
                advance();
                double right = parsePower();
                
                if (op == '*') {
                    result *= right;
                } else if (op == '/') {
                    if (right == 0) {
                        throw new ArithmeticException("Division by zero");
                    }
                    result /= right;
                } else {
                    if (right == 0) {
                        throw new ArithmeticException("Modulo by zero");
                    }
                    result %= right;
                }
            }
            
            return result;
        }
        
        // Parse exponentiation (higher precedence than multiplication)
        private double parsePower() {
            checkDepth();
            double result = parseFactor();
            
            if (currentChar == '^') {
                advance();
                double exponent = parsePower(); // Right associative
                result = Math.pow(result, exponent);
            }
            
            return result;
        }
        
        // Parse numbers, functions, and parentheses
        private double parseFactor() {
            checkDepth();
            skipWhitespace();
            
            // Handle unary minus
            if (currentChar == '-') {
                advance();
                return -parseFactor();
            }
            
            // Handle unary plus
            if (currentChar == '+') {
                advance();
                return parseFactor();
            }
            
            // Handle parentheses
            if (currentChar == '(') {
                advance();
                double result = parseExpression();
                if (currentChar != ')') {
                    throw new IllegalArgumentException("Missing closing parenthesis");
                }
                advance();
                return result;
            }
            
            // Handle functions
            if (Character.isLetter(currentChar)) {
                return parseFunction();
            }
            
            // Handle numbers
            if (Character.isDigit(currentChar) || currentChar == '.') {
                return parseNumber();
            }
            
            throw new IllegalArgumentException("Unexpected character: " + currentChar);
        }
        
        // Parse numeric values
        private double parseNumber() {
            StringBuilder sb = new StringBuilder();
            
            while (Character.isDigit(currentChar) || currentChar == '.') {
                sb.append(currentChar);
                advance();
            }
            
            try {
                return Double.parseDouble(sb.toString());
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Invalid number: " + sb.toString());
            }
        }
        
        // Parse function calls
        private double parseFunction() {
            StringBuilder funcName = new StringBuilder();
            
            while (Character.isLetter(currentChar)) {
                funcName.append(currentChar);
                advance();
            }
            
            String function = funcName.toString();
            
            // Validate function is in whitelist
            if (!ALLOWED_FUNCTIONS.contains(function)) {
                throw new SecurityException(
                    "Function '" + function + "' is not allowed. " +
                    "Allowed functions: " + ALLOWED_FUNCTIONS
                );
            }
            
            // Expect opening parenthesis
            if (currentChar != '(') {
                throw new IllegalArgumentException(
                    "Function '" + function + "' requires parentheses"
                );
            }
            advance();
            
            // Parse argument
            double arg = parseExpression();
            
            // Expect closing parenthesis
            if (currentChar != ')') {
                throw new IllegalArgumentException(
                    "Missing closing parenthesis for function '" + function + "'"
                );
            }
            advance();
            
            // Apply function
            return applyFunction(function, arg);
        }
        
        // Apply whitelisted mathematical functions
        private double applyFunction(String function, double arg) {
            switch (function) {
                case "sqrt":
                    if (arg < 0) {
                        throw new ArithmeticException("Cannot take square root of negative number");
                    }
                    return Math.sqrt(arg);
                case "abs":
                    return Math.abs(arg);
                case "sin":
                    return Math.sin(arg);
                case "cos":
                    return Math.cos(arg);
                case "tan":
                    return Math.tan(arg);
                case "log":
                    if (arg <= 0) {
                        throw new ArithmeticException("Logarithm undefined for non-positive numbers");
                    }
                    return Math.log10(arg);
                case "ln":
                    if (arg <= 0) {
                        throw new ArithmeticException("Natural logarithm undefined for non-positive numbers");
                    }
                    return Math.log(arg);
                case "exp":
                    return Math.exp(arg);
                case "ceil":
                    return Math.ceil(arg);
                case "floor":
                    return Math.floor(arg);
                case "round":
                    return Math.round(arg);
                default:
                    throw new SecurityException("Unknown function: " + function);
            }
        }
        
        // Prevent stack overflow from deeply nested expressions
        private void checkDepth() {
            currentDepth++;
            if (currentDepth > MAX_DEPTH) {
                throw new SecurityException(
                    "Expression too complex (max nesting depth: " + MAX_DEPTH + ")"
                );
            }
        }
    }
}