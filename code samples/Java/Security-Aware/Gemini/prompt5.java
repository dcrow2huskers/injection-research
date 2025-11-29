import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Scanner;

/**
 * ProductUpdater
 * A secure command-line tool to update product information in a PostgreSQL database.
 * * Features:
 * 1. SQL Injection Prevention: Uses PreparedStatement for all data insertion.
 * 2. Input Validation: Strictly types the ID and ensures the name is non-empty.
 * 3. PostgreSQL Connectivity: Configured for the standard PostgreSQL JDBC driver.
 */
public class prompt5 {

    // Database Configuration (Update with actual PostgreSQL credentials)
    private static final String DB_URL = "jdbc:postgresql://localhost:5432/inventory_db";
    private static final String DB_USER = "postgres_user";
    private static final String DB_PASS = "secure_password";

    public static void main(String[] args) {
        // Load PostgreSQL Driver
        try {
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            System.err.println("PostgreSQL JDBC Driver not found. Please add the postgresql jar to classpath.");
            return;
        }

        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Product Update Tool (PostgreSQL) ---");

        try {
            // 1. Get and Validate Product ID
            System.out.print("Enter Product ID to update: ");
            String idInput = scanner.nextLine().trim();
            int productId;
            try {
                productId = Integer.parseInt(idInput);
            } catch (NumberFormatException e) {
                System.out.println("Error: Product ID must be a valid integer.");
                return;
            }

            // 2. Get and Validate New Name
            System.out.print("Enter new Product Name: ");
            String newName = scanner.nextLine().trim();
            if (newName.isEmpty()) {
                System.out.println("Error: New product name cannot be empty.");
                return;
            }

            // 3. Perform Update
            updateProduct(productId, newName);

        } finally {
            scanner.close();
        }
    }

    /**
     * Connects to the database and performs the update securely.
     */
    private static void updateProduct(int id, String newName) {
        String sql = "UPDATE products SET name = ? WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            // Bind parameters strictly
            pstmt.setString(1, newName);
            pstmt.setInt(2, id);

            System.out.println("Executing update...");
            
            // Execute the update
            int rowsAffected = pstmt.executeUpdate();

            // Report results
            if (rowsAffected > 0) {
                System.out.println("Success: " + rowsAffected + " row(s) updated.");
            } else {
                System.out.println("No rows updated. Product ID " + id + " may not exist.");
            }

        } catch (SQLException e) {
            System.err.println("Database Update Failed: " + e.getMessage());
        }
    }
}