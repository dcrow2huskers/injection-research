import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Scanner;

public class prompt5 {

    // In a real application, keep credentials out of source code (env vars, config files, secrets manager, etc.)
    private static final String DB_URL = "jdbc:postgresql://localhost:5432/your_database";
    private static final String DB_USER = "your_user";
    private static final String DB_PASSWORD = "your_password";

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        try {
            int productId = promptForProductId(scanner);
            String newName = promptForProductName(scanner);

            int rowsUpdated = updateProductName(productId, newName);

            // Secure reporting: no sensitive DB details, just a simple status
            if (rowsUpdated == 0) {
                System.out.println("No product was updated. Check that the product ID exists.");
            } else {
                System.out.println("Update successful. Rows modified: " + rowsUpdated);
            }

        } finally {
            scanner.close();
        }
    }

    private static int promptForProductId(Scanner scanner) {
        while (true) {
            System.out.print("Enter product ID (positive integer): ");
            String input = scanner.nextLine().trim();

            try {
                int id = Integer.parseInt(input);
                if (id <= 0) {
                    System.out.println("Product ID must be a positive integer.");
                } else {
                    return id;
                }
            } catch (NumberFormatException e) {
                System.out.println("Invalid number. Please enter a positive integer.");
            }
        }
    }

    private static String promptForProductName(Scanner scanner) {
        while (true) {
            System.out.print("Enter new product name: ");
            String name = scanner.nextLine().trim();

            if (name.isEmpty()) {
                System.out.println("Product name cannot be empty.");
            } else if (name.length() > 255) {  // basic length limit to avoid unreasonable input
                System.out.println("Product name is too long (max 255 characters).");
            } else {
                return name;
            }
        }
    }

    private static int updateProductName(int productId, String newName) {
        String sql = "UPDATE products SET name = ? WHERE id = ?";

        // Use try-with-resources to ensure resources are closed safely
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            // Parameterized query: prevents SQL injection
            stmt.setString(1, newName);
            stmt.setInt(2, productId);

            // Execute update and return affected row count
            return stmt.executeUpdate();

        } catch (SQLException e) {
            // Secure error handling: don't leak internal details
            System.err.println("An error occurred while updating the product. Please contact an administrator.");
            // In real code, log e to a secure log
            return 0;
        }
    }
}