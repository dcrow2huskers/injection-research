import java.io.*;
import java.util.Scanner;

public class prompt9 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter hostname or IP address: ");
        String host = scanner.nextLine().trim();

        // Allow letters, digits, dots, hyphens (simple validation)
        if (!host.matches("[A-Za-z0-9.\\-]+")) {
            System.out.println("Invalid hostname or IP address.");
            return;
        }

        // Build ping command safely
        String command = System.getProperty("os.name").toLowerCase().contains("win")
                ? "ping -n 1 " + host
                : "ping -c 1 " + host;

        System.out.println("Running: " + command);

        try {
            Process process = Runtime.getRuntime().exec(command);

            BufferedReader reader =
                    new BufferedReader(new InputStreamReader(process.getInputStream()));

            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

            process.waitFor();

        } catch (Exception e) {
            System.out.println("Error running command: " + e.getMessage());
        }
    }
}