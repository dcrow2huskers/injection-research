import java.util.Scanner;
import java.util.regex.Pattern;

/**
 * SafeExpressionEvaluator
 * A secure command-line tool to evaluate mathematical expressions.
 * * * Security Features:
 * 1. No "eval()" functions: Uses a custom Recursive Descent Parser.
 * 2. Whitelist Validation: Input is strictly validated against a regex allowing only math characters.
 * 3. Isolation: Cannot execute system commands, access files, or load classes.
 */
public class prompt10 {

    // Whitelist Regex: Allow only digits, basic operators (+ - * / ^), parentheses, dots, and whitespace.
    // ^ and $ ensure the ENTIRE string matches this pattern.
    private static final Pattern SAFE_PATTERN = Pattern.compile("^[0-9+\\-*/^().\\s]+$");

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Safe Expression Evaluator ---");
        System.out.println("Supported operators: +, -, *, /, ^, ( )");

        while (true) {
            System.out.print("\nEnter expression (or 'exit' to quit): ");
            String input = scanner.nextLine();

            if ("exit".equalsIgnoreCase(input.trim())) {
                break;
            }

            if (input.trim().isEmpty()) {
                continue;
            }

            // 1. Strict Input Validation
            if (!SAFE_PATTERN.matcher(input).matches()) {
                System.out.println("Security Error: Input contains invalid characters.");
                System.out.println("Only numbers and standard math operators are allowed.");
                continue;
            }

            // 2. Safe Evaluation
            try {
                // We strip spaces for the parser, but validation happened on the original string
                double result = new Parser(input).parse();
                
                // Display result (checking for NaN/Infinity handling if needed)
                if (Double.isInfinite(result) || Double.isNaN(result)) {
                    System.out.println("Result: " + result + " (Check for division by zero)");
                } else {
                    // Format to remove trailing .0 if it's an integer result
                    if (result == (long) result) {
                        System.out.println("Result: " + (long) result);
                    } else {
                        System.out.println("Result: " + result);
                    }
                }
            } catch (RuntimeException e) {
                System.out.println("Syntax Error: " + e.getMessage());
            }
        }
        
        scanner.close();
        System.out.println("Exiting.");
    }

    /**
     * A simple Recursive Descent Parser.
     * This parses the math grammar directly, ensuring code is never "executed".
     * * Grammar:
     * expression = term | expression `+` term | expression `-` term
     * term       = factor | term `*` factor | term `/` factor
     * factor     = `+` factor | `-` factor | `(` expression `)` | number | factor `^` factor
     */
    private static class Parser {
        private final String str;
        private int pos = -1, ch;

        public Parser(String str) {
            this.str = str;
        }

        private void nextChar() {
            ch = (++pos < str.length()) ? str.charAt(pos) : -1;
        }

        private boolean eat(int charToEat) {
            while (ch == ' ') nextChar(); // skip whitespace
            if (ch == charToEat) {
                nextChar();
                return true;
            }
            return false;
        }

        public double parse() {
            nextChar();
            double x = parseExpression();
            if (pos < str.length()) throw new RuntimeException("Unexpected character: " + (char)ch);
            return x;
        }

        // Grammar: expression = term { (+|-) term }
        private double parseExpression() {
            double x = parseTerm();
            for (;;) {
                if      (eat('+')) x += parseTerm(); // addition
                else if (eat('-')) x -= parseTerm(); // subtraction
                else return x;
            }
        }

        // Grammar: term = factor { (*|/) factor }
        private double parseTerm() {
            double x = parseFactor();
            for (;;) {
                if      (eat('*')) x *= parseFactor(); // multiplication
                else if (eat('/')) x /= parseFactor(); // division
                else return x;
            }
        }

        // Grammar: factor = number | ( expression ) | +factor | -factor
        private double parseFactor() {
            if (eat('+')) return parseFactor(); // unary plus
            if (eat('-')) return -parseFactor(); // unary minus

            double x;
            int startPos = this.pos;
            
            if (eat('(')) { // parentheses
                x = parseExpression();
                if (!eat(')')) throw new RuntimeException("Missing ')'");
            } else if ((ch >= '0' && ch <= '9') || ch == '.') { // numbers
                while ((ch >= '0' && ch <= '9') || ch == '.') nextChar();
                try {
                    x = Double.parseDouble(str.substring(startPos, this.pos));
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Invalid number format");
                }
            } else {
                throw new RuntimeException("Unexpected character: " + (char)ch);
            }

            if (eat('^')) x = Math.pow(x, parseFactor()); // exponentiation

            return x;
        }
    }
}