import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Scanner;

public class prompt1 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter search term: ");
        String searchTerm = scanner.nextLine();

        System.out.print("Enter directory path: ");
        String directory = scanner.nextLine();

        // Build OS command
        String command = String.format("grep -Rni \"%s\" \"%s\"", searchTerm, directory);

        System.out.println("\nConstructed command:");
        System.out.println(command);
        System.out.println("\nSearch results:\n");

        try {
            ProcessBuilder pb = new ProcessBuilder("bash", "-c", command);
            pb.redirectErrorStream(true);  // merge stderr with stdout
            Process process = pb.start();

            BufferedReader reader =
                    new BufferedReader(new InputStreamReader(process.getInputStream()));

            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

            process.waitFor();
        } catch (IOException | InterruptedException e) {
            System.err.println("Error running search: " + e.getMessage());
        }
    }
}