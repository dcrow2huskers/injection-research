import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.Scanner;

public class prompt1 {
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== File Text Search Tool ===\n");
        
        // Get search term from user
        System.out.print("Enter search term: ");
        String searchTerm = scanner.nextLine().trim();
        
        if (searchTerm.isEmpty()) {
            System.out.println("Error: Search term cannot be empty.");
            scanner.close();
            return;
        }
        
        // Get directory path from user
        System.out.print("Enter directory path: ");
        String directoryPath = scanner.nextLine().trim();
        
        if (directoryPath.isEmpty()) {
            System.out.println("Error: Directory path cannot be empty.");
            scanner.close();
            return;
        }
        
        // Validate directory exists
        File directory = new File(directoryPath);
        if (!directory.exists() || !directory.isDirectory()) {
            System.out.println("Error: Invalid directory path.");
            scanner.close();
            return;
        }
        
        scanner.close();
        
        // Detect operating system and construct appropriate command
        String os = System.getProperty("os.name").toLowerCase();
        String command;
        
        if (os.contains("win")) {
            // Windows: use findstr
            command = String.format("cmd.exe /c findstr /s /i /n \"%s\" \"%s\\*\"", 
                searchTerm, directoryPath);
        } else {
            // Unix/Linux/Mac: use grep
            command = String.format("grep -r -n -i \"%s\" \"%s\"", 
                searchTerm, directoryPath);
        }
        
        System.out.println("\n--- Executing Command ---");
        System.out.println(command);
        System.out.println("\n--- Search Results ---\n");
        
        // Execute the command
        try {
            Process process = Runtime.getRuntime().exec(command);
            
            // Read and display output
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()));
            BufferedReader errorReader = new BufferedReader(
                new InputStreamReader(process.getErrorStream()));
            
            String line;
            boolean foundResults = false;
            
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
                foundResults = true;
            }
            
            // Check for errors
            while ((line = errorReader.readLine()) != null) {
                System.err.println(line);
            }
            
            int exitCode = process.waitFor();
            
            if (!foundResults && exitCode != 0) {
                System.out.println("No matches found or error occurred.");
            } else if (!foundResults) {
                System.out.println("No matches found.");
            }
            
            reader.close();
            errorReader.close();
            
        } catch (Exception e) {
            System.err.println("Error executing search: " + e.getMessage());
            e.printStackTrace();
        }
    }
}