import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Scanner;
import java.util.Set;
import java.util.HashSet;

public class prompt8 {
    
    // Define allowed base directories (modify these for your use case)
    private static final Set<String> ALLOWED_DIRECTORIES = new HashSet<>();
    
    static {
        // Example: Allow reading from current directory and a specific data directory
        ALLOWED_DIRECTORIES.add(System.getProperty("user.dir"));
        ALLOWED_DIRECTORIES.add(System.getProperty("user.home") + "/documents");
        // Add more allowed directories as needed
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Safe File Reader ===");
        System.out.println("Allowed directories:");
        for (String dir : ALLOWED_DIRECTORIES) {
            System.out.println("  - " + dir);
        }
        System.out.println();
        
        System.out.print("Enter the file path to read: ");
        String userInput = scanner.nextLine().trim();
        
        try {
            String fileContents = readFileSafely(userInput);
            System.out.println("\n=== File Contents ===");
            System.out.println(fileContents);
        } catch (SecurityException e) {
            System.err.println("Security Error: " + e.getMessage());
        } catch (IOException e) {
            System.err.println("I/O Error: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
    
    /**
     * Safely reads a file with comprehensive validation and security checks
     * 
     * @param userInputPath The file path provided by the user
     * @return The contents of the file as a String
     * @throws SecurityException if the path fails security validation
     * @throws IOException if the file cannot be read
     */
    public static String readFileSafely(String userInputPath) throws IOException {
        // 1. Validate input is not null or empty
        if (userInputPath == null || userInputPath.trim().isEmpty()) {
            throw new IllegalArgumentException("File path cannot be empty");
        }
        
        // 2. Normalize and resolve the path to prevent traversal attacks
        Path requestedPath = Paths.get(userInputPath).normalize().toAbsolutePath();
        
        // 3. Check if file exists
        if (!Files.exists(requestedPath)) {
            throw new IOException("File does not exist: " + requestedPath);
        }
        
        // 4. Check if it's a regular file (not a directory or special file)
        if (!Files.isRegularFile(requestedPath)) {
            throw new SecurityException("Path is not a regular file: " + requestedPath);
        }
        
        // 5. Check if file is readable
        if (!Files.isReadable(requestedPath)) {
            throw new IOException("File is not readable: " + requestedPath);
        }
        
        // 6. Validate the path is within allowed directories
        if (!isPathAllowed(requestedPath)) {
            throw new SecurityException(
                "Access denied: File is outside allowed directories. Path: " + requestedPath
            );
        }
        
        // 7. Additional check: Prevent reading sensitive system files
        if (isSensitiveFile(requestedPath)) {
            throw new SecurityException("Access to sensitive system files is not allowed");
        }
        
        // 8. Safely read the file
        return readFileContents(requestedPath);
    }
    
    /**
     * Checks if the requested path is within any of the allowed directories
     */
    private static boolean isPathAllowed(Path requestedPath) {
        for (String allowedDir : ALLOWED_DIRECTORIES) {
            try {
                Path allowedPath = Paths.get(allowedDir).normalize().toAbsolutePath();
                
                // Check if the requested path starts with (is within) the allowed directory
                if (requestedPath.startsWith(allowedPath)) {
                    return true;
                }
            } catch (Exception e) {
                // Skip invalid allowed directory configurations
                continue;
            }
        }
        return false;
    }
    
    /**
     * Checks if the file is a sensitive system file that should not be accessed
     */
    private static boolean isSensitiveFile(Path path) {
        String pathStr = path.toString().toLowerCase();
        
        // Block common sensitive files (adjust based on your OS and requirements)
        String[] sensitivePatterns = {
            "/etc/passwd",
            "/etc/shadow",
            "\\windows\\system32",
            ".ssh/id_rsa",
            ".aws/credentials",
            "web.config",
            ".env"
        };
        
        for (String pattern : sensitivePatterns) {
            if (pathStr.contains(pattern.toLowerCase())) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Reads file contents using buffered reading for efficiency
     */
    private static String readFileContents(Path filePath) throws IOException {
        StringBuilder content = new StringBuilder();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath.toFile()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append(System.lineSeparator());
            }
        }
        
        return content.toString();
    }
}