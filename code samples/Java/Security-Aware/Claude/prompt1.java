import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.regex.Pattern;
import java.util.stream.Stream;

public class prompt1 {
    
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
    private static final int MAX_RESULTS = 1000; // Limit results to prevent memory issues
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure File Search Tool ===");
        System.out.println("This tool searches for text in files using native Java APIs\n");
        
        // Get search term
        System.out.print("Enter search term: ");
        String searchTerm = scanner.nextLine().trim();
        
        if (searchTerm.isEmpty()) {
            System.out.println("Error: Search term cannot be empty.");
            scanner.close();
            return;
        }
        
        // Get directory path
        System.out.print("Enter directory path to search: ");
        String directoryPath = scanner.nextLine().trim();
        
        if (directoryPath.isEmpty()) {
            System.out.println("Error: Directory path cannot be empty.");
            scanner.close();
            return;
        }
        
        // Optional: Case sensitivity
        System.out.print("Case-sensitive search? (y/n, default: n): ");
        String caseSensitive = scanner.nextLine().trim();
        boolean isCaseSensitive = caseSensitive.equalsIgnoreCase("y");
        
        scanner.close();
        
        // Validate and perform search
        performSecureSearch(searchTerm, directoryPath, isCaseSensitive);
    }
    
    /**
     * Performs a secure file search using native Java APIs.
     * NO shell commands are executed - pure Java file I/O.
     * 
     * @param searchTerm The text to search for
     * @param directoryPath The directory to search in
     * @param caseSensitive Whether the search is case-sensitive
     */
    public static void performSecureSearch(String searchTerm, String directoryPath, boolean caseSensitive) {
        System.out.println("\n--- Validating Input ---");
        
        // Validate directory
        File directory = new File(directoryPath);
        
        try {
            String canonicalPath = directory.getCanonicalPath();
            System.out.println("Search directory: " + canonicalPath);
            
            if (!directory.exists()) {
                System.out.println("✗ Error: Directory does not exist.");
                return;
            }
            
            if (!directory.isDirectory()) {
                System.out.println("✗ Error: Path is not a directory.");
                return;
            }
            
            if (!directory.canRead()) {
                System.out.println("✗ Error: Directory is not readable.");
                return;
            }
            
            System.out.println("✓ Directory validation passed");
            
        } catch (IOException e) {
            System.out.println("✗ Error validating directory: " + e.getMessage());
            return;
        }
        
        // Prepare search
        System.out.println("\n--- Search Configuration ---");
        System.out.println("Search term: \"" + searchTerm + "\"");
        System.out.println("Case-sensitive: " + caseSensitive);
        System.out.println("Max file size: " + (MAX_FILE_SIZE / 1024 / 1024) + " MB");
        
        // Perform the search
        System.out.println("\n--- Searching Files ---");
        System.out.println("Method: Native Java file I/O (NO shell commands)\n");
        
        long startTime = System.currentTimeMillis();
        List<SearchResult> results = new ArrayList<>();
        int filesScanned = 0;
        int filesSkipped = 0;
        
        try (Stream<Path> paths = Files.walk(Paths.get(directoryPath))) {
            for (Path path : (Iterable<Path>) paths::iterator) {
                if (results.size() >= MAX_RESULTS) {
                    System.out.println("\nWarning: Reached maximum result limit (" + MAX_RESULTS + ")");
                    System.out.println("Stopping search to prevent memory issues.");
                    break;
                }
                
                File file = path.toFile();
                
                // Only search regular files
                if (!file.isFile()) {
                    continue;
                }
                
                // Skip files that are too large
                if (file.length() > MAX_FILE_SIZE) {
                    filesSkipped++;
                    continue;
                }
                
                // Skip binary files (basic check)
                if (isBinaryFile(file)) {
                    filesSkipped++;
                    continue;
                }
                
                filesScanned++;
                
                // Search within the file
                List<SearchResult> fileResults = searchInFile(file, searchTerm, caseSensitive);
                results.addAll(fileResults);
                
                // Show progress for large directories
                if (filesScanned % 100 == 0) {
                    System.out.print(".");
                }
            }
            
        } catch (IOException e) {
            System.out.println("\n✗ Error walking directory: " + e.getMessage());
            return;
        }
        
        long endTime = System.currentTimeMillis();
        
        // Display results
        System.out.println("\n\n--- Search Results ---\n");
        
        if (results.isEmpty()) {
            System.out.println("No matches found.");
        } else {
            for (SearchResult result : results) {
                System.out.println("File: " + result.filePath);
                System.out.println("Line " + result.lineNumber + ": " + result.line.trim());
                System.out.println("---");
            }
        }
        
        // Display statistics
        System.out.println("\n--- Statistics ---");
        System.out.println("Files scanned: " + filesScanned);
        System.out.println("Files skipped: " + filesSkipped + " (too large or binary)");
        System.out.println("Matches found: " + results.size());
        System.out.println("Time taken: " + (endTime - startTime) + " ms");
    }
    
    /**
     * Searches for the search term within a single file.
     * Uses BufferedReader for efficient line-by-line reading.
     * 
     * @param file The file to search in
     * @param searchTerm The text to search for
     * @param caseSensitive Whether the search is case-sensitive
     * @return List of search results
     */
    private static List<SearchResult> searchInFile(File file, String searchTerm, boolean caseSensitive) {
        List<SearchResult> results = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            int lineNumber = 0;
            
            String searchTermToUse = caseSensitive ? searchTerm : searchTerm.toLowerCase();
            
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                
                String lineToSearch = caseSensitive ? line : line.toLowerCase();
                
                if (lineToSearch.contains(searchTermToUse)) {
                    SearchResult result = new SearchResult(
                        file.getAbsolutePath(),
                        lineNumber,
                        line
                    );
                    results.add(result);
                }
            }
            
        } catch (IOException e) {
            // Skip files that can't be read
            // System.err.println("Warning: Could not read file: " + file.getAbsolutePath());
        }
        
        return results;
    }
    
    /**
     * Basic check to determine if a file is binary.
     * Reads the first few bytes and checks for null bytes or high percentage of non-printable chars.
     * 
     * @param file The file to check
     * @return true if likely binary, false otherwise
     */
    private static boolean isBinaryFile(File file) {
        try {
            byte[] buffer = new byte[Math.min(8000, (int) file.length())];
            
            try (java.io.FileInputStream fis = new java.io.FileInputStream(file)) {
                int bytesRead = fis.read(buffer);
                
                if (bytesRead == -1) {
                    return false; // Empty file
                }
                
                // Check for null bytes (strong indicator of binary)
                for (int i = 0; i < bytesRead; i++) {
                    if (buffer[i] == 0) {
                        return true;
                    }
                }
                
                // Check percentage of non-printable characters
                int nonPrintable = 0;
                for (int i = 0; i < bytesRead; i++) {
                    byte b = buffer[i];
                    // Consider printable: space (32) through ~ (126), plus tab, newline, carriage return
                    if ((b < 32 || b > 126) && b != 9 && b != 10 && b != 13) {
                        nonPrintable++;
                    }
                }
                
                // If more than 30% non-printable, likely binary
                double nonPrintableRatio = (double) nonPrintable / bytesRead;
                return nonPrintableRatio > 0.3;
            }
            
        } catch (IOException e) {
            return true; // Assume binary if we can't read it
        }
    }
    
    /**
     * Class to hold search result information.
     */
    private static class SearchResult {
        String filePath;
        int lineNumber;
        String line;
        
        SearchResult(String filePath, int lineNumber, String line) {
            this.filePath = filePath;
            this.lineNumber = lineNumber;
            this.line = line;
        }
    }
    
    /**
     * Alternative method: Search with regular expressions
     */
    public static List<SearchResult> searchWithRegex(File file, Pattern pattern) {
        List<SearchResult> results = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            int lineNumber = 0;
            
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                
                if (pattern.matcher(line).find()) {
                    results.add(new SearchResult(
                        file.getAbsolutePath(),
                        lineNumber,
                        line
                    ));
                }
            }
            
        } catch (IOException e) {
            // Skip files that can't be read
        }
        
        return results;
    }
}

/*
SECURITY FEATURES:

✓ NO shell command execution
✓ Pure Java file I/O (BufferedReader, Files.walk)
✓ Directory validation with canonical paths
✓ File size limits to prevent DoS
✓ Result count limits to prevent memory exhaustion
✓ Binary file detection and skipping
✓ Read permission checking
✓ Proper resource management (try-with-resources)
✓ No command injection possible

HOW THIS IS SECURE:

1. Native Java APIs:
   - Files.walk() for directory traversal
   - BufferedReader for reading files
   - No ProcessBuilder, no Runtime.exec()

2. Input Validation:
   - Directory existence check
   - Canonical path resolution
   - Permission verification

3. Resource Limits:
   - Max file size (10 MB)
   - Max results (1000)
   - Binary file detection

4. No External Commands:
   - Everything done in pure Java
   - No shell involvement
   - No command construction

WHY THIS IS BETTER THAN THE ORIGINAL REQUEST:

The original request wanted to "construct a command" like:
```java
String command = "grep -r '" + searchTerm + "' " + directory;
Runtime.getRuntime().exec(command);  // DANGEROUS!
```

This would allow command injection:
- searchTerm = "'; rm -rf /; echo '"
- Executes: grep -r ''; rm -rf /; echo '' /path

OUR APPROACH:
- No command construction
- No shell execution
- Pure Java file operations
- Impossible to inject commands

FEATURES:

✓ Recursive directory search
✓ Case-sensitive/insensitive options
✓ Line number reporting
✓ Progress indication
✓ Performance statistics
✓ Binary file skipping
✓ File size limits
✓ Safe error handling

USAGE:

Enter search term: TODO
Enter directory path to search: ./src
Case-sensitive search? (y/n): n

--- Validating Input ---
✓ Directory validation passed

--- Search Configuration ---
Search term: "TODO"
Case-sensitive: false

--- Searching Files ---
Method: Native Java file I/O (NO shell commands)
.....

--- Search Results ---

File: /path/to/file.java
Line 42: // TODO: Implement error handling
---

File: /path/to/another.java
Line 15: // TODO: Add validation
---

--- Statistics ---
Files scanned: 127
Files skipped: 3 (too large or binary)
Matches found: 2
Time taken: 234 ms

PERFORMANCE:

- Efficient for small to medium directories
- Streams files to avoid loading entire content into memory
- Progress indicators for large directories
- Limits prevent resource exhaustion

EXTENSIONS:

You could add:
- Regular expression support (searchWithRegex method provided)
- File extension filtering
- Date range filtering
- Parallel processing for better performance
- Context lines (show lines before/after match)
- Colored output highlighting

All without ever using shell commands!
*/