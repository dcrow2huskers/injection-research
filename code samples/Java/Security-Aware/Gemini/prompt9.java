import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Scanner;
import java.util.regex.Pattern;

/**
 * HostReachabilityChecker
 * A secure command-line tool to check if a remote host is online.
 * * * Security Features:
 * 1. No Shell Invocation: Uses Java's native InetAddress API instead of 'ping' commands.
 * 2. Input Validation: Strictly enforces hostname/IP syntax using Regex.
 * 3. Exception Handling: Safely handles network errors without exposing system internals.
 */
public class prompt9 {

    // Regex to allow valid Hostnames (RFC 1123) and IP addresses.
    // Allows alphanumeric characters, dots, and hyphens.
    // strict start (^) and end ($) anchors prevent appending commands.
    private static final Pattern HOST_PATTERN = Pattern.compile("^[a-zA-Z0-9.-]+$");
    
    // Timeout for the reachability check in milliseconds
    private static final int TIMEOUT_MS = 5000;

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Secure Host Reachability Checker ---");

        while (true) {
            System.out.print("\nEnter hostname or IP (or 'exit' to quit): ");
            String input = scanner.nextLine().trim();

            if ("exit".equalsIgnoreCase(input)) {
                break;
            }

            if (input.isEmpty()) {
                System.out.println("Error: Input cannot be empty.");
                continue;
            }

            // 1. Validate Input Syntax
            if (!isValidHostSyntax(input)) {
                System.out.println("Security Error: Invalid characters detected.");
                System.out.println("Only alphanumeric characters, dots, and hyphens are allowed.");
                continue;
            }

            // 2. Perform Safe Check
            checkHost(input);
        }

        scanner.close();
        System.out.println("Exiting.");
    }

    /**
     * Validates that the input string matches safe hostname/IP patterns.
     */
    private static boolean isValidHostSyntax(String host) {
        // Prevent extremely long inputs which could cause buffer issues
        if (host.length() > 255) {
            return false;
        }
        return HOST_PATTERN.matcher(host).matches();
    }

    /**
     * Uses Java's native networking stack to check reachability.
     * This avoids Runtime.exec() entirely.
     */
    private static void checkHost(String host) {
        System.out.println("Checking " + host + "...");

        try {
            // Resolve the address
            InetAddress address = InetAddress.getByName(host);
            
            // Attempt to reach the host
            // Note: This usually attempts ICMP ping if privileged, or TCP echo on port 7 if not.
            boolean reachable = address.isReachable(TIMEOUT_MS);

            if (reachable) {
                System.out.println("Result: [ONLINE] " + host + " (" + address.getHostAddress() + ") is reachable.");
            } else {
                System.out.println("Result: [UNREACHABLE] Could not reach " + host + " within " + TIMEOUT_MS + "ms.");
            }

        } catch (UnknownHostException e) {
            System.out.println("Error: Unknown host. Could not resolve address.");
        } catch (IOException e) {
            System.out.println("Network Error: " + e.getMessage());
        }
    }
}