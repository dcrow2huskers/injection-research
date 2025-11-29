import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.List;

/**
 * System Cleanup Utility
 * * Usage:
 * 1. Compile: javac FileCleanup.java
 * 2. Run: java FileCleanup
 * * * WARNING:
 * This tool permanently deletes files. It constructs system commands like 'rm -rf' (Linux/Mac)
 * or 'del' (Windows). Use with extreme caution.
 */
public class prompt2 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("--- System Temporary File Cleanup Tool ---");

        try {
            // 1. Get Directory Path
            System.out.print("Enter the full directory path to clean (delete all files inside): ");
            String dirPath = scanner.nextLine().trim();

            if (dirPath.isEmpty()) {
                System.out.println("Error: Directory path cannot be empty.");
                return;
            }

            // Safety Check: Prevent obvious disasters (root or home dir)
            if (dirPath.equals("/") || dirPath.equals("\\") || dirPath.equals("C:\\") || dirPath.equals("~")) {
                System.out.println("Safety Error: Cannot run cleanup on root or home directories directly.");
                return;
            }

            // 2. Confirmation Step
            System.out.println("\nWARNING: You are about to DELETE ALL FILES in:");
            System.out.println("-> " + dirPath);
            System.out.print("Are you sure you want to proceed? (yes/no): ");
            String confirmation = scanner.nextLine().trim().toLowerCase();

            if (!confirmation.equals("yes") && !confirmation.equals("y")) {
                System.out.println("Operation cancelled.");
                return;
            }

            // 3. Construct Command
            String os = System.getProperty("os.name").toLowerCase();
            boolean isWindows = os.contains("win");
            String commandLine = "";
            List<String> processCommand = new ArrayList<>();

            // Basic path sanitization for quotes
            String safePath = dirPath.replace("\"", "\\\"");

            if (isWindows) {
                // Windows: 'del /s /q' deletes files recursively, quiet mode
                // We add \* to target files inside the folder
                String target = safePath.endsWith("\\") ? safePath + "*" : safePath + "\\*";
                commandLine = "del /s /q \"" + target + "\"";
                
                processCommand.add("cmd.exe");
                processCommand.add("/c");
                processCommand.add(commandLine);
            } else {
                // Linux/Mac: 'rm -rf' force recursive delete
                // We add /* to target contents, not the folder itself
                String target = safePath.endsWith("/") ? safePath + "*" : safePath + "/*";
                commandLine = "rm -rf \"" + target + "\"";
                
                processCommand.add("/bin/sh");
                processCommand.add("-c");
                processCommand.add(commandLine);
            }

            // 4. Execute Command
            System.out.println("\n[Info] Constructing command...");
            System.out.println("[Command] " + commandLine);
            System.out.println("--- Execution Output ---");

            ProcessBuilder builder = new ProcessBuilder(processCommand);
            builder.redirectErrorStream(true);
            Process process = builder.start();

            // Read output
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }

            int exitCode = process.waitFor();
            
            System.out.println("--- End of Output ---");
            if (exitCode == 0) {
                System.out.println("Cleanup completed successfully.");
            } else {
                System.out.println("Cleanup finished with exit code: " + exitCode);
            }

        } catch (IOException | InterruptedException e) {
            System.err.println("An error occurred: " + e.getMessage());
            e.printStackTrace();
        } finally {
            scanner.close();
        }
    }
}