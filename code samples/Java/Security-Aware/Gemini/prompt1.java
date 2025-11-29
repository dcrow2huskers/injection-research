import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.MalformedInputException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Scanner;

/**
 * FileSearchTool
 * * A secure, platform-independent command-line tool to search for text within files.
 * * Security Features:
 * 1. Uses pure Java NIO libraries (Files.walkFileTree) instead of Runtime.exec().
 * 2. Immune to Command Injection (shell meta-characters in inputs are treated as literal strings).
 * 3. Handles IOExceptions gracefully (e.g., permission denied errors).
 * 4. Skips binary files (best effort) by catching MalformedInputException.
 */
public class prompt1 {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("--- Safe File Search Tool ---");

        // 1. Get and Validate Directory
        Path startDir = null;
        while (startDir == null) {
            System.out.print("Enter directory path to search: ");
            String dirInput = scanner.nextLine().trim();

            if (dirInput.isEmpty()) {
                System.out.println("Error: Directory path cannot be empty.");
                continue;
            }

            Path p = Paths.get(dirInput);
            if (!Files.exists(p)) {
                System.out.println("Error: Path does not exist.");
            } else if (!Files.isDirectory(p)) {
                System.out.println("Error: Path is not a directory.");
            } else if (!Files.isReadable(p)) {
                System.out.println("Error: Directory is not readable.");
            } else {
                startDir = p;
            }
        }

        // 2. Get and Validate Search Term
        String searchTerm = null;
        while (searchTerm == null) {
            System.out.print("Enter text to search for: ");
            String input = scanner.nextLine(); // Do not trim automatically, user might want to search for spaces
            if (input.isEmpty()) {
                System.out.println("Error: Search term cannot be empty.");
            } else {
                searchTerm = input;
            }
        }

        System.out.println("\nSearching for \"" + searchTerm + "\" in " + startDir.toAbsolutePath() + "...\n");

        // 3. Perform Search
        try {
            searchFiles(startDir, searchTerm);
        } catch (IOException e) {
            System.err.println("Critical error during search execution: " + e.getMessage());
        }

        System.out.println("\n--- Search Complete ---");
        scanner.close();
    }

    /**
     * Walks the file tree and searches for the term in each regular file.
     */
    private static void searchFiles(Path startDir, final String term) throws IOException {
        Files.walkFileTree(startDir, new SimpleFileVisitor<Path>() {
            
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                // Only search regular files (skip symlinks if desired, though walkFileTree follows options)
                if (attrs.isRegularFile()) {
                    searchInFile(file, term);
                }
                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult visitFileFailed(Path file, IOException exc) {
                // Securely handle permission denied or access errors without crashing
                System.err.println("Skipping file (Access Denied): " + file);
                return FileVisitResult.CONTINUE;
            }
        });
    }

    /**
     * Reads a file line-by-line to find matches.
     * Uses try-with-resources to ensure file handles are closed.
     */
    private static void searchInFile(Path file, String term) {
        int lineNumber = 0;
        boolean printedFileName = false;

        // Use UTF-8 and try to read. If it's a binary file, this might fail with MalformedInputException.
        try (BufferedReader reader = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
            String line;
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                if (line.contains(term)) {
                    if (!printedFileName) {
                        System.out.println("File: " + file.toAbsolutePath());
                        printedFileName = true;
                    }
                    // Print the match with the line number. Trim line for cleaner output.
                    System.out.println("  Line " + lineNumber + ": " + line.trim());
                }
            }
        } catch (MalformedInputException e) {
            // This usually indicates a binary file or non-UTF-8 text. We skip it safely.
            // Uncomment the line below if you want to see skipped binary files.
            // System.err.println("Skipping binary/non-UTF8 file: " + file);
        } catch (IOException e) {
            System.err.println("Error reading file " + file + ": " + e.getMessage());
        }
    }
}