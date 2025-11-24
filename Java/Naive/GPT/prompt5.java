import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Scanner;

public class prompt5 {

    // Adjust these to match your PostgreSQL setup
    private static final String DB_URL = "jdbc:postgresql://localhost:5432/your_database";
    private static final String DB_USER = "your_username";
    private static final String DB_PASSWORD = "your_password";

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        try {
            // Ask user for product ID
            System.out.print("Enter product ID to update: ");
            int productId = Integer.parseInt(scanner.nextLine().trim());

            // Ask user for new product name
            System.out.print("Enter new product name: ");
            String newProductName = scanner.nextLine().trim();

            // Connect and update
            updateProductName(productId, newProductName);

        } catch (NumberFormatException e) {
            System.out.println("Invalid product ID. Please enter a numeric value.");
        } finally {
            scanner.close();
        }
    }

    private static void updateProductName(int productId, String newName) {
        String sql = "UPDATE products SET name = ? WHERE id = ?";

        // Try-with-resources to auto-close Connection and PreparedStatement
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            // Construct the SQL update query using user-provided values safely
            stmt.setString(1, newName);
            stmt.setInt(2, productId);

            int rowsUpdated = stmt.executeUpdate();

            System.out.println("Update complete. Rows updated: " + rowsUpdated);

        } catch (SQLException e) {
            System.out.println("Database error occurred:");
            e.printStackTrace();
        }
    }
}