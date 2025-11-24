import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;

public class prompt8 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter a filename or full file path: ");
        String path = scanner.nextLine().trim();

        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            System.out.println("\n--- File Contents ---");
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
            System.out.println("--- End of File ---");
        } catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
        }
    }
}