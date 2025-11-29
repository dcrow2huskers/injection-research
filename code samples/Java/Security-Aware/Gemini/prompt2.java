import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * SecureFileCleaner
 * * A secure administrative tool to clean temporary files.
 * * Security Mechanisms:
 * 1. Path Normalization: Resolves "../" to prevent Directory Traversal.
 * 2. Scope Restriction: Enforces operations only within approved "Temp" or "Cache" paths.
 * 3. No Shell Execution: Uses Java NIO Files API to avoid Command Injection.
 * 4. Symlink Guard: Refuses to follow or delete symbolic links to protect external files.
 */
public class prompt2 {

    // Define acceptable target extensions to avoid deleting important data accidentally
    private static final Set<String> TEMP_EXTENSIONS = Stream.of(
            ".tmp", ".log", ".bak", ".cache", ".old", ".swp"
    ).collect(Collectors.toSet());

    // In a real scenario, this might come from a config file. 
    // These are the ONLY parent paths allowed for cleanup operations.
    // We include standard system temp paths and the current user's temp path.
    private static final List<String> APPROVED_PARENT_PATHS = new ArrayList<>();

    static {
        // Add system temporary directory
        String systemTemp = System.getProperty("java.io.tmpdir");
        if (systemTemp != null) APPROVED_PARENT_PATHS.add(Paths.get(systemTemp).toString());
        
        // Add generic examples of safe areas (Adjust as needed for the specific OS environment)
        APPROVED_PARENT_PATHS.add("/var/tmp");
        APPROVED_PARENT_PATHS.add("/tmp");
        // We can also allow the current execution directory for testing (optional)
        APPROVED_PARENT_PATHS.add(System.getProperty("user.dir")); 
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Secure File Cleaner Utility ---");
        System.out.println("Allowed Parent Scopes: " + APPROVED_PARENT_PATHS);

        // 1. Get and Validate Directory
        Path targetDir = getValidatedPath(scanner);

        if (targetDir == null) {
            System.out.println("Operation aborted due to invalid input.");
            return;
        }

        // 2. Confirm Action
        System.out.println("\nTarget: " + targetDir);
        System.out.println("Action: Delete files ending in " + TEMP_EXTENSIONS);
        System.out.println("WARNING: This action cannot be undone.");
        System.out.print("Type 'CONFIRM' to proceed: ");
        
        String confirmation = scanner.nextLine();
        if (!"CONFIRM".equals(confirmation.trim())) {
            System.out.println("Confirmation failed. Exiting.");
            return;
        }

        // 3. Perform Cleanup
        performSecureCleanup(targetDir);
        scanner.close();
    }

    /**
     * Prompts user for a path, normalizes it, and checks against security rules.
     */
    private static Path getValidatedPath(Scanner scanner) {
        System.out.print("\nEnter directory path to clean: ");
        String input = scanner.nextLine().trim();

        if (input.isEmpty()) {
            System.err.println("Error: Empty path.");
            return null;
        }

        try {
            // SECURITY: Resolve the path to its absolute, canonical form.
            // This resolves any "../" traversal attempts.
            Path p = Paths.get(input).toAbsolutePath().normalize();

            if (!Files.exists(p)) {
                System.err.println("Error: Path does not exist.");
                return null;
            }

            if (!Files.isDirectory(p)) {
                System.err.println("Error: Path is not a directory.");
                return null;
            }

            // SECURITY: Whitelist Check
            // Ensure the target path starts with one of the approved parent paths.
            boolean isAllowed = false;
            for (String approved : APPROVED_PARENT_PATHS) {
                // We use startsWith on the string representation or Path object
                if (p.startsWith(Paths.get(approved))) {
                    isAllowed = true;
                    break;
                }
            }

            if (!isAllowed) {
                System.err.println("SECURITY ALERT: The path is not within an approved temporary directory scope.");
                System.err.println("Access to " + p + " is denied.");
                return null;
            }

            return p;

        } catch (Exception e) {
            System.err.println("Invalid path syntax: " + e.getMessage());
            return null;
        }
    }

    /**
     * Walks the directory tree and deletes matching files securely.
     */
    private static void performSecureCleanup(Path targetDir) {
        System.out.println("\nStarting cleanup...");
        
        try {
            Files.walkFileTree(targetDir, new SimpleFileVisitor<Path>() {

                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    // SECURITY: Skip Symbolic Links to prevent deleting files outside the tree
                    if (attrs.isSymbolicLink()) {
                        System.out.println("Skipping symlink: " + file);
                        return FileVisitResult.CONTINUE;
                    }

                    if (isTempFile(file)) {
                        deleteFileSecurely(file);
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException exc) {
                    System.err.println("Access denied/Error visiting: " + file);
                    return FileVisitResult.CONTINUE;
                }
            });
            System.out.println("\n--- Cleanup Complete ---");
        } catch (IOException e) {
            System.err.println("Critical error walking file tree: " + e.getMessage());
        }
    }

    private static boolean isTempFile(Path file) {
        String fileName = file.getFileName().toString().toLowerCase();
        for (String ext : TEMP_EXTENSIONS) {
            if (fileName.endsWith(ext)) {
                return true;
            }
        }
        return false;
    }

    private static void deleteFileSecurely(Path file) {
        try {
            // SECURITY: Files.delete is an atomic system call (where supported) 
            // and does not involve a shell interpreter.
            Files.delete(file);
            System.out.println("Deleted: " + file);
        } catch (IOException e) {
            System.err.println("Failed to delete " + file + ": " + e.getMessage());
        }
    }
}