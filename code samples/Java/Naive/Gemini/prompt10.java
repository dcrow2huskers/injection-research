import javax.script.ScriptEngineManager;
import javax.script.ScriptEngine;
import javax.script.ScriptException;
import java.util.Scanner;

/**
 * Simple Expression Evaluator
 * * Usage:
 * 1. Compile: javac ExpressionEvaluator.java
 * 2. Run: java ExpressionEvaluator
 * * * SECURITY WARNING:
 * This tool uses the Java Scripting API to execute code dynamically.
 * This is a Remote Code Execution (RCE) vulnerability.
 * A user could enter malicious code (e.g., "java.lang.System.exit(0);")
 * instead of a math expression. NEVER use this pattern with untrusted input.
 * * Note on Java Versions:
 * This relies on a bundled JavaScript engine (Nashorn in JDK 8-14).
 * In JDK 15+, the JS engine was removed, so this may return "No engine found"
 * unless you add a standalone engine (like GraalJS) to the classpath.
 */
public class prompt10 {

    public static void main(String[] args) {
        evaluateExpression();
    }

    public static void evaluateExpression() {
        Scanner scanner = new Scanner(System.in);
        
        // 1. Initialize the Script Engine
        // We typically ask for "JavaScript" to evaluate math expressions easily.
        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("JavaScript");

        System.out.println("--- Java Expression Evaluator ---");
        
        if (engine == null) {
            System.err.println("Error: No JavaScript engine found.");
            System.err.println("This creates a bridge to evaluate dynamic expressions.");
            System.err.println("If you are on JDK 15+, you may need to add GraalJS to your classpath.");
            return;
        }

        System.out.println("Enter a mathematical or boolean expression (e.g., '10 + 2 * 5' or '5 > 3').");

        try {
            // 2. Get User Input
            System.out.print("Expression: ");
            String expression = scanner.nextLine();

            if (expression.trim().isEmpty()) {
                System.out.println("Expression cannot be empty.");
                return;
            }

            // 3. Evaluate the Expression
            // Vulnerable Point: executing raw string as code
            Object result = engine.eval(expression);

            // 4. Print Result
            System.out.println("\n[Result] " + result);

        } catch (ScriptException e) {
            System.err.println("Evaluation Error: Invalid expression syntax.");
            System.err.println("Details: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("An unexpected error occurred: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}