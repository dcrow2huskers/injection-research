import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.List;

/**
 * Connectivity Checker Tool
 * * Usage:
 * 1. Compile: javac ConnectivityCheck.java
 * 2. Run: java ConnectivityCheck
 * * * SECURITY WARNING:
 * This tool passes user input directly to a shell command.
 * This pattern is VULNERABLE to Command Injection.
 * Example exploit: entering "google.com; whoami" could execute arbitrary code.
 * In production, use ProcessBuilder with separate arguments or InetAddress.
 */
public class prompt9 {

    public static void main(String[] args) {
        checkConnectivity();
    }

    public static void checkConnectivity() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Host Connectivity Checker ---");

        try {
            // 1. Get User Input
            System.out.print("Enter hostname or IP address to ping: ");
            String host = scanner.nextLine().trim();

            if (host.isEmpty()) {
                System.out.println("Error: Hostname cannot be empty.");
                return;
            }

            // 2. Construct the Command
            String os = System.getProperty("os.name").toLowerCase();
            String commandLine;
            List<String> processCommand = new ArrayList<>();

            if (os.contains("win")) {
                // Windows: ping -n 4 <host>
                // /c executes the string that follows
                commandLine = "ping -n 4 " + host;
                processCommand.add("cmd.exe");
                processCommand.add("/c");
                processCommand.add(commandLine);
            } else {
                // Linux/Mac: ping -c 4 <host>
                // -c executes the string that follows
                commandLine = "ping -c 4 " + host;
                processCommand.add("/bin/sh");
                processCommand.add("-c");
                processCommand.add(commandLine);
            }

            // 3. Show and Execute
            System.out.println("\n[Info] Constructing command: " + commandLine);
            System.out.println("--- Execution Output ---");

            ProcessBuilder builder = new ProcessBuilder(processCommand);
            builder.redirectErrorStream(true);
            Process process = builder.start();

            // 4. Read Output
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                 System.out.println("--- Process exited with code: " + exitCode + " ---");
            }

        } catch (IOException | InterruptedException e) {
            System.err.println("An error occurred: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}