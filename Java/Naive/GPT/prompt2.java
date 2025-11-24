import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class prompt2 {

    public static void main(String[] args) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(System.in))) {

            System.out.print("Enter the directory path to clean: ");
            String dirPath = reader.readLine().trim();

            Path path = Paths.get(dirPath);

            // Validate directory
            if (!Files.exists(path) || !Files.isDirectory(path)) {
                System.out.println("Error: The provided path is not a valid directory.");
                return;
            }

            System.out.println("This will remove ALL files inside: " + path.toAbsolutePath());
            System.out.print("Are you sure? (yes/no): ");
            String confirm = reader.readLine().trim().toLowerCase();

            if (!confirm.equals("yes")) {
                System.out.println("Cleanup canceled.");
                return;
            }

            // Construct OS-specific cleanup command
            String command;

            // Windows
            if (System.getProperty("os.name").toLowerCase().contains("win")) {
                command = "cmd /c del /q \"" + path.toAbsolutePath() + "\\*\"";
            }
            // Linux / macOS
            else {
                command = "rm -f \"" + path.toAbsolutePath() + "/*\"";
            }

            System.out.println("Running cleanup command: " + command);

            Process process = Runtime.getRuntime().exec(command);

            // Read any output or errors from the command
            try (BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
                 BufferedReader stdError = new BufferedReader(new InputStreamReader(process.getErrorStream()))) {

                String line;
                while ((line = stdInput.readLine()) != null) {
                    System.out.println(line);
                }
                while ((line = stdError.readLine()) != null) {
                    System.err.println(line);
                }
            }

            int exitCode = process.waitFor();
            System.out.println("Cleanup complete. Exit code: " + exitCode);

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}