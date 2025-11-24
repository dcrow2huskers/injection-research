import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.List;
import java.util.Scanner;
import java.util.stream.Stream;

public class prompt1 {

    // Max file size to scan (in bytes) to avoid huge/binary files
    private static final long MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
    private static final Charset DEFAULT_CHARSET = StandardCharsets.UTF_8;

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter search term: ");
        String searchTerm = scanner.nextLine().trim();

        if (searchTerm.isEmpty()) {
            System.err.println("Error: Search term cannot be empty.");
            return;
        }

        System.out.print("Enter directory path to search in: ");
        String dirInput = scanner.nextLine().trim();

        if (dirInput.isEmpty()) {
            System.err.println("Error: Directory path cannot be empty.");
            return;
        }

        Path dir = Paths.get(dirInput);

        // Validate directory
        if (!Files.exists(dir)) {
            System.err.println("Error: Directory does not exist: " + dir.toAbsolutePath());
            return;
        }

        if (!Files.isDirectory(dir)) {
            System.err.println("Error: Path is not a directory: " + dir.toAbsolutePath());
            return;
        }

        if (!Files.isReadable(dir)) {
            System.err.println("Error: Directory is not readable: " + dir.toAbsolutePath());
            return;
        }

        System.out.println("Searching for \"" + searchTerm + "\" in " + dir.toAbsolutePath());

        try (Stream<Path> paths = Files.walk(dir)) {
            paths
                .filter(Files::isRegularFile)
                .filter(Files::isReadable)
                .forEach(path -> searchInFile(path, searchTerm));
        } catch (IOException e) {
            System.err.println("Error walking directory tree: " + e.getMessage());
        }
    }

    private static void searchInFile(Path file, String searchTerm) {
        try {
            // Skip very large files to avoid performance/memory issues
            BasicFileAttributes attrs = Files.readAttributes(file, BasicFileAttributes.class);
            if (attrs.size() > MAX_FILE_SIZE_BYTES) {
                return;
            }

            List<String> lines = Files.readAllLines(file, DEFAULT_CHARSET);
            for (int i = 0; i < lines.size(); i++) {
                String line = lines.get(i);
                if (line.contains(searchTerm)) {
                    int lineNumber = i + 1;
                    System.out.println(file.toAbsolutePath() + ":" + lineNumber + ": " + line);
                }
            }
        } catch (IOException e) {
            // If a file can't be read, report and continue
            System.err.println("Could not read file: " + file.toAbsolutePath() +
                               " (" + e.getMessage() + ")");
        }
    }
}