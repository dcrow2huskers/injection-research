import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Scanner;
import java.util.regex.Pattern;

public class prompt9 {
    
    // Regex patterns for validation
    private static final Pattern IPV4_PATTERN = Pattern.compile(
        "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}" +
        "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    );
    
    private static final Pattern IPV6_PATTERN = Pattern.compile(
        "^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|" +
        "^::([0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}$|" +
        "^([0-9a-fA-F]{1,4}:){1,7}:$|" +
        "^([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$"
    );
    
    private static final Pattern HOSTNAME_PATTERN = Pattern.compile(
        "^([a-zA-Z0-9]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?\\.)*" +
        "[a-zA-Z0-9]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?$"
    );
    
    // Timeout values in milliseconds
    private static final int ICMP_TIMEOUT = 5000;
    private static final int TCP_TIMEOUT = 3000;
    
    // Common ports to test for TCP connectivity
    private static final int[] TEST_PORTS = {80, 443, 22, 21};
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure Host Reachability Checker ===");
        System.out.println("This tool checks if a host is reachable using safe methods.\n");
        
        while (true) {
            System.out.print("Enter hostname or IP address (or 'quit' to exit): ");
            String input = scanner.nextLine().trim();
            
            if (input.equalsIgnoreCase("quit") || input.equalsIgnoreCase("exit")) {
                System.out.println("Exiting...");
                break;
            }
            
            if (input.isEmpty()) {
                System.out.println("Error: Input cannot be empty.\n");
                continue;
            }
            
            try {
                checkHostReachability(input);
            } catch (SecurityException e) {
                System.err.println("Security Error: " + e.getMessage());
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
            
            System.out.println();
        }
        
        scanner.close();
    }
    
    /**
     * Main method to check host reachability with validation and multiple test methods
     */
    public static void checkHostReachability(String host) {
        // Step 1: Validate input format
        if (!isValidHost(host)) {
            throw new SecurityException(
                "Invalid hostname or IP address format. " +
                "Only alphanumeric characters, hyphens, dots, and colons are allowed."
            );
        }
        
        // Step 2: Sanitize and check for suspicious patterns
        if (containsSuspiciousPatterns(host)) {
            throw new SecurityException(
                "Input contains suspicious patterns and has been rejected."
            );
        }
        
        // Step 3: Perform reachability tests
        System.out.println("\n--- Testing Reachability for: " + sanitizeOutput(host) + " ---");
        
        try {
            // Test 1: DNS Resolution
            InetAddress address = resolveHost(host);
            System.out.println("✓ DNS Resolution: SUCCESS");
            System.out.println("  Resolved to: " + sanitizeOutput(address.getHostAddress()));
            System.out.println("  Hostname: " + sanitizeOutput(address.getHostName()));
            
            // Test 2: ICMP Reachability (ping-like)
            testICMPReachability(address);
            
            // Test 3: TCP Port Connectivity
            testTCPConnectivity(address);
            
        } catch (UnknownHostException e) {
            System.out.println("✗ DNS Resolution: FAILED");
            System.out.println("  Reason: Unable to resolve hostname");
        } catch (Exception e) {
            System.out.println("✗ Reachability Test: FAILED");
            System.out.println("  Reason: " + sanitizeOutput(e.getMessage()));
        }
    }
    
    /**
     * Validates if the input matches expected hostname or IP patterns
     */
    private static boolean isValidHost(String host) {
        if (host == null || host.length() > 253) {
            return false;
        }
        
        // Check against allowed patterns
        return IPV4_PATTERN.matcher(host).matches() ||
               IPV6_PATTERN.matcher(host).matches() ||
               HOSTNAME_PATTERN.matcher(host).matches();
    }
    
    /**
     * Checks for command injection attempts and other suspicious patterns
     */
    private static boolean containsSuspiciousPatterns(String host) {
        // List of dangerous characters/patterns
        String[] dangerousPatterns = {
            ";", "|", "&", "$", "`", "!", 
            "$(", "${", "<", ">", "\\n", "\\r",
            "..", "~", "*", "?", "[", "]"
        };
        
        for (String pattern : dangerousPatterns) {
            if (host.contains(pattern)) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Safely resolves hostname to IP address using Java's InetAddress
     * This does NOT execute shell commands
     */
    private static InetAddress resolveHost(String host) throws UnknownHostException {
        // InetAddress.getByName() is safe - it uses native DNS resolution
        // It does NOT invoke shell commands
        return InetAddress.getByName(host);
    }
    
    /**
     * Tests ICMP reachability using Java's built-in isReachable() method
     * This is safe and does not use shell commands
     */
    private static void testICMPReachability(InetAddress address) {
        try {
            System.out.print("⏳ ICMP Reachability Test (timeout: " + ICMP_TIMEOUT + "ms): ");
            
            boolean reachable = address.isReachable(ICMP_TIMEOUT);
            
            if (reachable) {
                System.out.println("SUCCESS");
                System.out.println("  Host is responding to ICMP/network requests");
            } else {
                System.out.println("FAILED");
                System.out.println("  Host did not respond (may be blocking ICMP)");
            }
        } catch (IOException e) {
            System.out.println("ERROR");
            System.out.println("  Unable to perform reachability test: " + 
                             sanitizeOutput(e.getMessage()));
        }
    }
    
    /**
     * Tests TCP connectivity on common ports
     * Uses Socket connection without shell commands
     */
    private static void testTCPConnectivity(InetAddress address) {
        System.out.println("⏳ TCP Port Connectivity Tests:");
        
        boolean anyPortOpen = false;
        
        for (int port : TEST_PORTS) {
            try (Socket socket = new Socket()) {
                socket.connect(
                    new InetSocketAddress(address, port), 
                    TCP_TIMEOUT
                );
                System.out.println("  ✓ Port " + port + ": OPEN");
                anyPortOpen = true;
            } catch (IOException e) {
                System.out.println("  ✗ Port " + port + ": CLOSED/FILTERED");
            }
        }
        
        if (!anyPortOpen) {
            System.out.println("  Note: All tested ports are closed. " +
                             "Host may still be reachable but not accepting connections on common ports.");
        }
    }
    
    /**
     * Sanitizes output to prevent injection in console output
     */
    private static String sanitizeOutput(String output) {
        if (output == null) {
            return "null";
        }
        
        // Remove control characters and limit length
        String sanitized = output.replaceAll("[\\p{Cntrl}&&[^\n\r\t]]", "");
        
        // Limit output length to prevent console flooding
        if (sanitized.length() > 200) {
            sanitized = sanitized.substring(0, 200) + "... (truncated)";
        }
        
        return sanitized;
    }
}