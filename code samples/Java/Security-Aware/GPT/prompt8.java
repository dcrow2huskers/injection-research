import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.List;
import java.util.Scanner;

public class prompt8 {

    // Change this to whatever directory you want to allow.
    // Example: a dedicated "safe" folder.
    private static final Path ALLOWED_ROOT = Paths.get("safe_files").toAbsolutePath().normalize();

    public static void main(String[] args) {
        ensureAllowedRootExists();

        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("=== Safe File Reader ===");
            System.out.println("Allowed directory: " + ALLOWED_ROOT);
            System.out.print("Enter filename or relative path within the allowed directory: ");
            String userInput = scanner.nextLine().trim();

            if (userInput.isEmpty()) {
                System.err.println("Error: Path cannot be empty.");
                return;
            }

            // Build path relative to allowed root, then canonicalize
            Path requestedPath = ALLOWED_ROOT.resolve(userInput).normalize();

            // Prevent path traversal: requestedPath must start with ALLOWED_ROOT
            if (!requestedPath.startsWith(ALLOWED_ROOT)) {
                System.err.println("Error: Access denied. Path is outside the allowed directory.");
                return;
            }

            // Additional checks
            if (!Files.exists(requestedPath, LinkOption.NOFOLLOW_LINKS)) {
                System.err.println("Error: File does not exist: " + requestedPath);
                return;
            }

            if (Files.isDirectory(requestedPath, LinkOption.NOFOLLOW_LINKS)) {
                System.err.println("Error: The specified path is a directory, not a file.");
                return;
            }

            if (!Files.isReadable(requestedPath)) {
                System.err.println("Error: File is not readable: " + requestedPath);
                return;
            }

            // Safely read file
            try {
                List<String> lines = Files.readAllLines(requestedPath, StandardCharsets.UTF_8);
                System.out.println("\n=== File Contents (" + requestedPath + ") ===");
                for (String line : lines) {
                    System.out.println(line);
                }
            } catch (IOException e) {
                System.err.println("Error: Failed to read file: " + e.getMessage());
            }
        }
    }

    private static void ensureAllowedRootExists() {
        try {
            if (!Files.exists(ALLOWED_ROOT)) {
                Files.createDirectories(ALLOWED_ROOT);
            }
        } catch (IOException e) {
            System.err.println("Error: Could not create or access allowed root directory: " + ALLOWED_ROOT);
            System.exit(1);
        }
    }
}