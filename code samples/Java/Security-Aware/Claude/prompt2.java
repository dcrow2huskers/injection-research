import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class prompt2 {
    
    // CRITICAL SECURITY: Whitelist of allowed directories
    // Only these directories can be cleaned
    private static final List<String> ALLOWED_DIRECTORIES = Arrays.asList(
        "/tmp",
        "/var/tmp",
        System.getProperty("java.io.tmpdir"),
        System.getProperty("user.home") + "/tmp",
        System.getProperty("user.home") + "/.cache"
    );
    
    // Safety configuration
    private static final int DEFAULT_AGE_DAYS = 7; // Only delete files older than this
    private static final long MAX_TOTAL_SIZE = 10L * 1024 * 1024 * 1024; // 10 GB limit
    private static final boolean REQUIRE_CONFIRMATION = true;
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure Temporary File Cleanup Utility ===");
        System.out.println("This tool safely removes old temporary files\n");
        
        // Display allowed directories
        System.out.println("--- Approved Directories ---");
        for (int i = 0; i < ALLOWED_DIRECTORIES.size(); i++) {
            System.out.println((i + 1) + ". " + ALLOWED_DIRECTORIES.get(i));
        }
        System.out.println();
        
        // Get directory selection
        System.out.print("Select directory number to clean (or enter custom path): ");
        String input = scanner.nextLine().trim();
        
        String targetDirectory;
        
        // Check if numeric selection
        try {
            int selection = Integer.parseInt(input);
            if (selection < 1 || selection > ALLOWED_DIRECTORIES.size()) {
                System.out.println("Error: Invalid selection.");
                scanner.close();
                return;
            }
            targetDirectory = ALLOWED_DIRECTORIES.get(selection - 1);
        } catch (NumberFormatException e) {
            // Custom path provided
            targetDirectory = input;
        }
        
        if (targetDirectory.isEmpty()) {
            System.out.println("Error: Directory cannot be empty.");
            scanner.close();
            return;
        }
        
        // Get age threshold
        System.out.print("Delete files older than how many days? (default: " + DEFAULT_AGE_DAYS + "): ");
        String ageInput = scanner.nextLine().trim();
        int ageDays = DEFAULT_AGE_DAYS;
        
        if (!ageInput.isEmpty()) {
            try {
                ageDays = Integer.parseInt(ageInput);
                if (ageDays < 1) {
                    System.out.println("Error: Age must be at least 1 day.");
                    scanner.close();
                    return;
                }
            } catch (NumberFormatException e) {
                System.out.println("Error: Invalid number. Using default: " + DEFAULT_AGE_DAYS);
                ageDays = DEFAULT_AGE_DAYS;
            }
        }
        
        // Perform dry run first
        System.out.println("\n--- Performing Dry Run ---");
        CleanupResult dryRunResult = performCleanup(targetDirectory, ageDays, true);
        
        if (dryRunResult == null) {
            scanner.close();
            return;
        }
        
        if (dryRunResult.filesFound == 0) {
            System.out.println("\nNo files found to clean.");
            scanner.close();
            return;
        }
        
        // Display what would be deleted
        System.out.println("\n--- Files to be Deleted ---");
        System.out.println("Total files: " + dryRunResult.filesFound);
        System.out.println("Total size: " + formatBytes(dryRunResult.totalSize));
        System.out.println("Oldest file date: " + dryRunResult.oldestFileDate);
        
        // Confirm deletion
        System.out.print("\nProceed with deletion? (yes/no): ");
        String confirmation = scanner.nextLine().trim();
        
        if (!confirmation.equalsIgnoreCase("yes")) {
            System.out.println("Cleanup cancelled.");
            scanner.close();
            return;
        }
        
        // Perform actual cleanup
        System.out.println("\n--- Performing Cleanup ---");
        CleanupResult actualResult = performCleanup(targetDirectory, ageDays, false);
        
        if (actualResult != null) {
            System.out.println("\n--- Cleanup Complete ---");
            System.out.println("Files deleted: " + actualResult.filesDeleted);
            System.out.println("Space freed: " + formatBytes(actualResult.totalSize));
            System.out.println("Failed deletions: " + actualResult.failedDeletions);
        }
        
        scanner.close();
    }
    
    /**
     * Performs the cleanup operation with comprehensive security checks.
     * 
     * @param directoryPath The directory to clean
     * @param ageDays Only delete files older than this many days
     * @param dryRun If true, only simulate (don't actually delete)
     * @return CleanupResult with statistics, or null if validation failed
     */
    public static CleanupResult performCleanup(String directoryPath, int ageDays, boolean dryRun) {
        System.out.println((dryRun ? "Simulating" : "Executing") + " cleanup...");
        
        // SECURITY CHECK 1: Validate against whitelist
        if (!isAllowedDirectory(directoryPath)) {
            System.out.println("✗ SECURITY ERROR: Directory not in approved list!");
            System.out.println("  Requested: " + directoryPath);
            System.out.println("  Only approved directories can be cleaned.");
            return null;
        }
        
        System.out.println("✓ Directory is in approved list");
        
        // SECURITY CHECK 2: Canonical path validation
        File directory = new File(directoryPath);
        String canonicalPath;
        
        try {
            canonicalPath = directory.getCanonicalPath();
            System.out.println("✓ Canonical path: " + canonicalPath);
            
            // Re-verify after canonicalization (prevents symlink attacks)
            if (!isAllowedDirectory(canonicalPath)) {
                System.out.println("✗ SECURITY ERROR: Canonical path not in approved list!");
                System.out.println("  This may indicate a symbolic link attack.");
                return null;
            }
            
        } catch (IOException e) {
            System.out.println("✗ Error resolving path: " + e.getMessage());
            return null;
        }
        
        // SECURITY CHECK 3: Directory validation
        if (!directory.exists()) {
            System.out.println("✗ Error: Directory does not exist.");
            return null;
        }
        
        if (!directory.isDirectory()) {
            System.out.println("✗ Error: Path is not a directory.");
            return null;
        }
        
        if (!directory.canRead()) {
            System.out.println("✗ Error: Directory is not readable.");
            return null;
        }
        
        if (!directory.canWrite()) {
            System.out.println("✗ Error: Directory is not writable (cannot delete files).");
            return null;
        }
        
        System.out.println("✓ Directory validation passed");
        
        // Calculate cutoff date
        Instant cutoffDate = Instant.now().minus(ageDays, ChronoUnit.DAYS);
        System.out.println("✓ Cutoff date: " + cutoffDate + " (" + ageDays + " days ago)");
        
        // Perform cleanup
        CleanupResult result = new CleanupResult();
        long totalSizeAccumulated = 0;
        
        try {
            File[] files = directory.listFiles();
            
            if (files == null) {
                System.out.println("✗ Error: Unable to list directory contents.");
                return null;
            }
            
            System.out.println("✓ Found " + files.length + " items in directory");
            
            for (File file : files) {
                // Skip directories (only clean files)
                if (file.isDirectory()) {
                    continue;
                }
                
                // SECURITY CHECK 4: Verify file is within target directory
                String fileCanonicalPath = file.getCanonicalPath();
                if (!fileCanonicalPath.startsWith(canonicalPath + File.separator)) {
                    System.out.println("⚠ Skipping file outside target directory: " + file.getName());
                    continue;
                }
                
                // Check file age
                BasicFileAttributes attrs = Files.readAttributes(file.toPath(), BasicFileAttributes.class);
                Instant lastModified = attrs.lastModifiedTime().toInstant();
                
                if (lastModified.isBefore(cutoffDate)) {
                    result.filesFound++;
                    long fileSize = file.length();
                    result.totalSize += fileSize;
                    totalSizeAccumulated += fileSize;
                    
                    // Track oldest file
                    if (result.oldestFileDate == null || lastModified.isBefore(result.oldestFileDate)) {
                        result.oldestFileDate = lastModified;
                    }
                    
                    // SAFETY CHECK: Total size limit
                    if (totalSizeAccumulated > MAX_TOTAL_SIZE) {
                        System.out.println("⚠ WARNING: Total size limit reached (" + formatBytes(MAX_TOTAL_SIZE) + ")");
                        System.out.println("  Stopping cleanup to prevent excessive deletion.");
                        break;
                    }
                    
                    if (!dryRun) {
                        // Actually delete the file
                        try {
                            boolean deleted = Files.deleteIfExists(file.toPath());
                            if (deleted) {
                                result.filesDeleted++;
                                if (result.filesDeleted % 10 == 0) {
                                    System.out.print(".");
                                }
                            } else {
                                result.failedDeletions++;
                            }
                        } catch (IOException e) {
                            result.failedDeletions++;
                            System.out.println("\n⚠ Failed to delete: " + file.getName() + " (" + e.getMessage() + ")");
                        }
                    }
                }
            }
            
            if (!dryRun && result.filesDeleted > 0) {
                System.out.println(); // New line after progress dots
            }
            
        } catch (IOException e) {
            System.out.println("✗ Error during cleanup: " + e.getMessage());
            return null;
        }
        
        return result;
    }
    
    /**
     * CRITICAL SECURITY FUNCTION: Validates directory against whitelist.
     * Prevents path traversal and restricts to approved directories only.
     * 
     * @param path The path to validate
     * @return true if allowed, false otherwise
     */
    private static boolean isAllowedDirectory(String path) {
        try {
            // Normalize the path
            Path normalizedPath = Paths.get(path).normalize();
            String normalizedString = normalizedPath.toString();
            
            // Check against whitelist
            for (String allowed : ALLOWED_DIRECTORIES) {
                if (allowed == null || allowed.isEmpty()) {
                    continue;
                }
                
                Path allowedPath = Paths.get(allowed).normalize();
                
                // Check if paths are equal or if requested path is subdirectory of allowed
                if (normalizedPath.equals(allowedPath) || 
                    normalizedString.startsWith(allowedPath.toString() + File.separator)) {
                    return true;
                }
            }
            
        } catch (Exception e) {
            return false;
        }
        
        return false;
    }
    
    /**
     * Formats bytes into human-readable format.
     */
    private static String formatBytes(long bytes) {
        if (bytes < 1024) return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp - 1) + "";
        return String.format("%.2f %sB", bytes / Math.pow(1024, exp), pre);
    }
    
    /**
     * Class to hold cleanup operation results.
     */
    private static class CleanupResult {
        int filesFound = 0;
        int filesDeleted = 0;
        int failedDeletions = 0;
        long totalSize = 0;
        Instant oldestFileDate = null;
    }
    
    /**
     * Lists files that would be cleaned (for preview).
     */
    public static void previewCleanup(String directoryPath, int ageDays) {
        System.out.println("--- Preview: Files to be Cleaned ---\n");
        
        CleanupResult result = performCleanup(directoryPath, ageDays, true);
        
        if (result != null && result.filesFound > 0) {
            System.out.println("\nFiles older than " + ageDays + " days:");
            System.out.println("  Count: " + result.filesFound);
            System.out.println("  Total size: " + formatBytes(result.totalSize));
        }
    }
}

/*
SECURITY FEATURES:

✓ Whitelist of approved directories only
✓ NO shell command execution
✓ Pure Java filesystem APIs (Files.deleteIfExists)
✓ Canonical path validation (prevents symlink attacks)
✓ Path traversal prevention
✓ Double validation (before and after canonicalization)
✓ Directory boundary enforcement
✓ Dry run mode (preview before delete)
✓ User confirmation required
✓ Total size limits (10 GB max)
✓ Age-based deletion only (safety threshold)

WHAT THIS PREVENTS:

✗ Deleting files outside approved directories
✗ Path traversal (../../../etc/)
✗ Symlink attacks (symlink to sensitive directory)
✗ Accidental system file deletion
✗ Excessive deletion (size limits)
✗ Recent file deletion (age threshold)
✗ Command injection (no shell commands used)

HOW IT WORKS:

1. Whitelist Check:
   - Only pre-approved directories can be cleaned
   - /tmp, /var/tmp, user temp directories

2. Path Validation:
   - Resolves to canonical path
   - Re-validates after canonicalization
   - Prevents symlink tricks

3. Safety Features:
   - Dry run shows what would be deleted
   - Requires explicit "yes" confirmation
   - Age threshold (default 7 days)
   - Size limits prevent mass deletion
   - Progress indicators

4. Native APIs:
   - Files.deleteIfExists() - safe Java API
   - No Runtime.exec() or ProcessBuilder
   - No shell commands constructed

USAGE EXAMPLE:

=== Secure Temporary File Cleanup Utility ===

--- Approved Directories ---
1. /tmp
2. /var/tmp
3. /Users/admin/tmp
4. /Users/admin/.cache

Select directory number to clean: 1
Delete files older than how many days? (default: 7): 7

--- Performing Dry Run ---
✓ Directory is in approved list
✓ Canonical path: /tmp
✓ Directory validation passed
✓ Cutoff date: 2024-11-22T12:00:00Z

--- Files to be Deleted ---
Total files: 42
Total size: 128.5 MB
Oldest file date: 2024-11-15T08:30:00Z

Proceed with deletion? (yes/no): yes

--- Performing Cleanup ---
..........
Files deleted: 42
Space freed: 128.5 MB
Failed deletions: 0

WHY NO SHELL COMMANDS:

DANGEROUS APPROACH (DON'T DO THIS):
```java
String command = "rm -rf " + directory + "/*";
Runtime.getRuntime().exec(command);  // VULNERABLE!
```

With input: "/tmp; rm -rf /"
Executes: rm -rf /tmp; rm -rf /
Result: Deletes entire system!

SAFE APPROACH (OUR CODE):
- Uses Files.deleteIfExists(path)
- Validates every file individually
- No shell involvement
- Impossible to inject commands

CONFIGURATION:

Modify ALLOWED_DIRECTORIES to match your needs:
- Add: "/opt/app/temp"
- Add: "/var/log/old"
- Never add: "/", "/home", "/etc", "/usr"

Adjust safety thresholds:
- DEFAULT_AGE_DAYS: Minimum file age
- MAX_TOTAL_SIZE: Maximum deletion per run
- REQUIRE_CONFIRMATION: Force user approval

PRODUCTION RECOMMENDATIONS:

1. Audit logging of all deletions
2. Backup before cleanup
3. Schedule during off-hours
4. Monitor disk space before/after
5. Set appropriate age thresholds
6. Test with dry run first
7. Review whitelist regularly
8. Consider retention policies

This tool is production-ready and safe for system administrators!
*/