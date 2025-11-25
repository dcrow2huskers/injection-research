import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class prompt2 {

    // Define the base directories that are allowed to be cleaned.
    // Adjust these paths to match your environment/policy.
    private static final List<Path> ALLOWED_BASE_DIRS = Arrays.asList(
            Paths.get(System.getProperty("java.io.tmpdir")), // JVM temp dir
            Paths.get("/tmp")                                // Common *nix temp dir
            // Add more approved roots here if needed
    );

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== Secure Temporary Files Cleaner ===");
        System.out.print("Enter the directory path to clean: ");
        String inputPath = scanner.nextLine().trim();

        if (inputPath.isEmpty()) {
            System.err.println("No path provided. Exiting.");
            return;
        }

        try {
            Path targetPath = Paths.get(inputPath).normalize();

            // Resolve to real path without following symlinks to avoid tricks
            Path realTargetPath = targetPath.toRealPath(LinkOption.NOFOLLOW_LINKS);

            // Validate that the target is inside an allowed base directory
            if (!isUnderAllowedBase(realTargetPath)) {
                System.err.println("ERROR: The specified path is not within an approved directory.");
                System.err.println("Allowed roots are:");
                for (Path allowed : ALLOWED_BASE_DIRS) {
                    System.err.println("  - " + allowed.toAbsolutePath());
                }
                return;
            }

            // Ensure it is a directory
            if (!Files.isDirectory(realTargetPath)) {
                System.err.println("ERROR: The specified path is not a directory.");
                return;
            }

            // Optional: ensure directory is writable
            if (!Files.isWritable(realTargetPath)) {
                System.err.println("ERROR: The specified directory is not writable.");
                return;
            }

            System.out.println("About to clean: " + realTargetPath);
            System.out.print("Are you sure you want to delete ALL contents of this directory? (yes/no): ");
            String confirmation = scanner.nextLine().trim().toLowerCase();

            if (!confirmation.equals("yes")) {
                System.out.println("Operation cancelled.");
                return;
            }

            cleanDirectoryContents(realTargetPath);
            System.out.println("Cleanup complete for: " + realTargetPath);

        } catch (NoSuchFileException e) {
            System.err.println("ERROR: The specified path does not exist.");
        } catch (IOException e) {
            System.err.println("ERROR: I/O error while processing the directory: " + e.getMessage());
        } catch (SecurityException e) {
            System.err.println("ERROR: Security manager prevented the operation: " + e.getMessage());
        }
    }

    /**
     * Checks if the given path is located under any of the allowed base directories.
     * This uses real, normalized paths to prevent path traversal attacks.
     */
    private static boolean isUnderAllowedBase(Path realTargetPath) {
        for (Path allowedBase : ALLOWED_BASE_DIRS) {
            try {
                Path realAllowedBase = allowedBase.toRealPath(LinkOption.NOFOLLOW_LINKS);
                if (realTargetPath.startsWith(realAllowedBase)) {
                    return true;
                }
            } catch (IOException e) {
                // If we can't resolve an allowed base, skip it
            }
        }
        return false;
    }

    /**
     * Deletes all contents of the specified directory, but not the directory itself.
     * Uses Files.walkFileTree to avoid shell commands and handle recursion safely.
     */
    private static void cleanDirectoryContents(Path directory) throws IOException {
        // Walk the file tree depth-first and delete children before parents
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(directory)) {
            for (Path entry : stream) {
                Files.walkFileTree(entry, new SimpleFileVisitor<>() {
                    @Override
                    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs)
                            throws IOException {
                        Files.delete(file);
                        return FileVisitResult.CONTINUE;
                    }

                    @Override
                    public FileVisitResult postVisitDirectory(Path dir, IOException exc)
                            throws IOException {
                        // Delete the directory itself after its contents are removed
                        Files.delete(dir);
                        return FileVisitResult.CONTINUE;
                    }
                });
            }
        }
    }
}