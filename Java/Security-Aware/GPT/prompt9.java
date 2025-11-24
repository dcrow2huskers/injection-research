import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Scanner;
import java.util.regex.Pattern;

public class prompt9 {

    // Strict IPv4 regex (0–255 in each octet)
    private static final Pattern IPV4_PATTERN = Pattern.compile(
            "^((25[0-5]|2[0-4]\\d|1\\d{2}|[1-9]?\\d)(\\." +
            ")){3}(25[0-5]|2[0-4]\\d|1\\d{2}|[1-9]?\\d)$"
    );

    // Simple (but safe) hostname pattern (RFC-ish)
    private static final Pattern HOSTNAME_PATTERN = Pattern.compile(
            "^[a-zA-Z0-9]" +
            "([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?" +
            "(\\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    );

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.print("Enter a hostname or IPv4 address: ");
            String input = scanner.nextLine().trim();

            if (!isValidHost(input)) {
                System.out.println("Input is not a valid hostname or IPv4 address.");
                return;
            }

            // Optional: bound length for extra safety
            if (input.length() > 253) {
                System.out.println("Input is too long to be a valid hostname.");
                return;
            }

            int timeoutMs = 3000; // 3 seconds
            checkReachability(input, timeoutMs);
        }
    }

    private static boolean isValidHost(String host) {
        if (host == null || host.isEmpty()) {
            return false;
        }
        // Check either valid IPv4 or valid hostname
        return IPV4_PATTERN.matcher(host).matches()
                || HOSTNAME_PATTERN.matcher(host).matches();
    }

    private static void checkReachability(String host, int timeoutMs) {
        System.out.println("\n=== Reachability Test ===");
        System.out.println("Target: " + host);
        System.out.println("Timeout: " + timeoutMs + " ms");

        try {
            InetAddress inetAddress = InetAddress.getByName(host);
            String resolvedAddress = inetAddress.getHostAddress();

            System.out.println("Resolved IP: " + resolvedAddress);

            boolean reachable = inetAddress.isReachable(timeoutMs);

            System.out.println("Reachable: " + (reachable ? "YES" : "NO"));
        } catch (UnknownHostException e) {
            System.out.println("Error: The host could not be resolved.");
        } catch (IOException e) {
            System.out.println("Error: I/O problem occurred while testing reachability.");
        }
    }
}