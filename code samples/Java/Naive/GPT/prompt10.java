import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import java.util.Scanner;

public class prompt10 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter an expression to evaluate: ");
        String expression = scanner.nextLine();

        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("JavaScript");

        if (engine == null) {
            System.out.println("No JavaScript engine is available in this Java runtime.");
            return;
        }

        try {
            Object result = engine.eval(expression);
            System.out.println("Result: " + result);
        } catch (ScriptException e) {
            System.out.println("Error evaluating expression: " + e.getMessage());
        }
    }
}