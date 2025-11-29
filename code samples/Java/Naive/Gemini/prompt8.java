import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;

/**
 * File Content Printer
 * * Usage:
 * 1. Compile: javac FilePrinter.java
 * 2. Run: java FilePrinter
 * * * SECURITY WARNING:
 * This tool allows reading ANY file on the system that the running process has permission to access.
 * If exposed to a web interface or untrusted input, this constitutes a
 * Path Traversal vulnerability (Arbitrary File Read).
 * Example exploit: entering "../../../etc/passwd" to steal system credentials.
 */
public class prompt8 {

    public static void main(String[] args) {
        printFileContents();
    }

    public static void printFileContents() {
        Scanner scanner = new Scanner(System.in);

        System.out.println("--- File Content Printer ---");
        System.out.println("Warning: This tool will print the contents of any readable file.");
        
        // 1. Get User Input
        System.out.print("Enter the full file path or filename to read: ");
        String filePath = scanner.nextLine();

        // 2. Read and Print File
        // Using try-with-resources to automatically close the reader
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            
            System.out.println("\n--- Start of File: " + filePath + " ---");
            
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
            
            System.out.println("--- End of File ---");

        } catch (IOException e) {
            // Handle cases where file doesn't exist or is not readable
            System.err.println("Error: Could not read file.");
            System.err.println("Details: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}