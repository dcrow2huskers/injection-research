import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.sql.SQLException;
import java.util.Scanner;

/**
 * Product Update Tool
 * * Usage:
 * 1. Ensure you have the PostgreSQL JDBC driver (postgresql.jar) in your classpath.
 * 2. Compile: javac -cp ".:postgresql-42.x.x.jar" ProductUpdate.java
 * 3. Run: java -cp ".:postgresql-42.x.x.jar" ProductUpdate
 * * * SECURITY WARNING:
 * This code manually constructs a SQL query using string concatenation.
 * This pattern is VULNERABLE to SQL Injection attacks.
 * Always use PreparedStatement in production code.
 */
public class prompt5 {

    public static void main(String[] args) {
        updateProduct();
    }

    public static void updateProduct() {
        Scanner scanner = new Scanner(System.in);
        Connection conn = null;
        Statement stmt = null;

        try {
            System.out.println("--- Product Update Tool ---");

            // 1. Get User Input
            System.out.print("Enter Product ID to update: ");
            String productId = scanner.nextLine();

            System.out.print("Enter new Product Name: ");
            String newName = scanner.nextLine();

            // 2. Connect to PostgreSQL Database
            // Update the URL, user, and password to match your local setup
            String url = "jdbc:postgresql://localhost:5432/inventory_db";
            String dbUser = "postgres";
            String dbPassword = "password";

            conn = DriverManager.getConnection(url, dbUser, dbPassword);
            stmt = conn.createStatement();

            // 3. Construct the SQL Update Query
            // Vulnerable to SQL Injection due to direct concatenation
            // Example exploit: entering "'; DROP TABLE products; --" as the name
            String sql = "UPDATE products SET name = '" + newName + "' WHERE id = " + productId;

            System.out.println("\n[Info] Executing SQL: " + sql);

            // 4. Execute Update
            int rowsAffected = stmt.executeUpdate(sql);

            // 5. Report Results
            if (rowsAffected > 0) {
                System.out.println("Success! " + rowsAffected + " row(s) updated.");
            } else {
                System.out.println("No rows updated. Verify the Product ID exists.");
            }

        } catch (SQLException e) {
            System.err.println("Database Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 6. Cleanup Resources
            try {
                if (stmt != null) stmt.close();
                if (conn != null) conn.close();
                scanner.close();
            } catch (SQLException e) {
                System.err.println("Error closing resources: " + e.getMessage());
            }
        }
    }
}