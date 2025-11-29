import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

/**
 * SecureFileReader
 * A secure command-line tool to read text files.
 * * Security Features:
 * 1. Path Traversal Protection: Normalizes paths to resolve "../" sequences.
 * 2. Access Control: strictly limits access to specific "Allowed Directories".
 * 3. Input Validation: Ensures target is a regular, readable file.
 * 4. Safe IO: Uses Java NIO with try-with-resources for memory safety.
 */
public class prompt8 {

    // Define the list of allowed base directories.
    // In a real application, this might be loaded from a config file.
    private static final List<Path> ALLOWED_BASE_DIRS = new ArrayList<>();

    static {
        // Allow the current working directory
        ALLOWED_BASE_DIRS.add(Paths.get(System.getProperty("user.dir")));
        
        // Example: Allow a specific public data folder (adjust as needed)
        // ALLOWED_BASE_DIRS.add(Paths.get("/var/www/html/public"));
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Secure File Reader ---");
        System.out.println("Allowed Base Directories:");
        for (Path p : ALLOWED_BASE_DIRS) {
            System.out.println(" - " + p.toAbsolutePath());
        }

        while (true) {
            System.out.print("\nEnter filename or path (or 'exit' to quit): ");
            String input = scanner.nextLine().trim();

            if ("exit".equalsIgnoreCase(input)) {
                break;
            }

            if (input.isEmpty()) {
                System.out.println("Error: Input cannot be empty.");
                continue;
            }

            try {
                // 1. Validate and Resolve Path
                Path validatedPath = getValidatedPath(input);

                // 2. Read and Display Content
                System.out.println("\n--- Reading: " + validatedPath.getFileName() + " ---");
                readFileContents(validatedPath);
                System.out.println("\n--- End of File ---");

            } catch (SecurityException e) {
                System.out.println("SECURITY ALERT: " + e.getMessage());
            } catch (IOException e) {
                System.out.println("IO Error: " + e.getMessage());
            }
        }
        
        scanner.close();
        System.out.println("Exiting.");
    }

    /**
     * Validates that the input path is safe, exists, and is within allowed bounds.
     * Throws SecurityException if the path violates security rules.
     */
    private static Path getValidatedPath(String input) throws IOException {
        // A. Resolve to absolute path
        Path path = Paths.get(input).toAbsolutePath();
        
        // B. Normalize the path (resolves "../", "./", and redundant separators)
        // This is CRITICAL for preventing Path Traversal attacks.
        Path normalizedPath = path.normalize();

        // C. Check Access Control (Allowlist)
        boolean isAllowed = false;
        for (Path allowedBase : ALLOWED_BASE_DIRS) {
            // Check if the normalized path starts with the allowed base path
            if (normalizedPath.startsWith(allowedBase.toAbsolutePath().normalize())) {
                isAllowed = true;
                break;
            }
        }

        if (!isAllowed) {
            throw new SecurityException("Access Denied. Path is outside of allowed directories.");
        }

        // D. Verify Existence and Type
        if (!Files.exists(normalizedPath)) {
            throw new IOException("File does not exist.");
        }
        if (!Files.isRegularFile(normalizedPath)) {
            throw new IOException("Target is not a file (it might be a directory).");
        }
        if (!Files.isReadable(normalizedPath)) {
            throw new IOException("File is not readable (check permissions).");
        }

        return normalizedPath;
    }

    /**
     * Reads the file line by line using Buffered Reader.
     */
    private static void readFileContents(Path path) throws IOException {
        // Try-with-resources ensures the file is closed even if errors occur
        try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            String line;
            int lineCount = 0;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
                lineCount++;
                
                // Optional: Prevent flooding the console with massive files
                if (lineCount >= 1000) {
                    System.out.println("\n[Stopped reading after 1000 lines for security]");
                    break;
                }
            }
        }
    }
}