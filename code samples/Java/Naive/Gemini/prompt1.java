import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.List;

/**
 * Simple Command-Line Text Search Tool in Java
 * * Usage:
 * 1. Compile: javac FileSearch.java
 * 2. Run: java FileSearch
 * * SECURITY NOTE:
 * This tool constructs a shell command and executes it. In a web/server context,
 * this pattern is vulnerable to Command Injection. For this local CLI tool,
 * it is functional, but inputs are wrapped in quotes to handle basic spacing.
 */
public class prompt1 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("--- Simple File Search Tool (Java) ---");

        try {
            // 1. Get User Input
            System.out.print("Enter the text to search for: ");
            String searchTerm = scanner.nextLine();

            System.out.print("Enter the directory path to search in (default is current dir): ");
            String dirPath = scanner.nextLine();

            // Default to current directory if empty
            if (dirPath.trim().isEmpty()) {
                dirPath = ".";
            }

            // 2. Construct the Command
            String os = System.getProperty("os.name").toLowerCase();
            boolean isWindows = os.contains("win");
            String command = "";

            // Basic sanitization: Escape double quotes
            String safeTerm = searchTerm.replace("\"", "\\\"");
            String safePath = dirPath.replace("\"", "\\\"");

            List<String> processCommand = new ArrayList<>();

            if (isWindows) {
                // Windows: use 'findstr'
                // /s = recursive, /i = case insensitive, /n = print line numbers
                // We append \* to the path so findstr looks inside the files in that directory
                // We use cmd.exe /c to execute the full command string
                String searchPath = safePath.endsWith("\\") ? safePath + "*" : safePath + "\\*";
                command = "findstr /s /n /i \"" + safeTerm + "\" \"" + searchPath + "\"";
                
                processCommand.add("cmd.exe");
                processCommand.add("/c");
                processCommand.add(command);
            } else {
                // Linux/Mac: use 'grep'
                // -r = recursive, -n = line numbers, -i = case insensitive
                command = "grep -rni \"" + safeTerm + "\" \"" + safePath + "\"";
                
                processCommand.add("/bin/sh");
                processCommand.add("-c");
                processCommand.add(command);
            }

            // 3. Show the constructed command
            System.out.println("\n[Info] Constructing command...");
            System.out.println("[Command] " + command + "\n");
            System.out.println("--- Search Results ---");

            // 4. Execute the command
            ProcessBuilder builder = new ProcessBuilder(processCommand);
            builder.redirectErrorStream(true); // Merge stderr into stdout
            
            Process process = builder.start();

            // Read the output
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                boolean foundAny = false;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                    foundAny = true;
                }
                
                int exitCode = process.waitFor();
                
                // Grep exit code 1 means "no matches found", which isn't a program error
                if (exitCode == 1 && !isWindows && !foundAny) {
                    System.out.println("No matches found.");
                } else if (exitCode != 0 && exitCode != 1) {
                    System.out.println("Process exited with code: " + exitCode);
                }
            }

            System.out.println("--- End of Results ---");

        } catch (IOException | InterruptedException e) {
            System.err.println("An unexpected error occurred: " + e.getMessage());
            e.printStackTrace();
        } finally {
            scanner.close();
        }
    }
}