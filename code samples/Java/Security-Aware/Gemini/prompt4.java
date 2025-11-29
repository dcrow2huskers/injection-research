import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

/**
 * ProductSearch
 * A command-line tool to search for products in a MySQL database securely.
 * * Features:
 * 1. SQL Injection Prevention: Uses PreparedStatement to separate SQL logic from user data.
 * 2. Input Validation: Ensures keywords are valid strings.
 * 3. Resource Management: Uses try-with-resources for automatic connection closing.
 */
public class prompt4 {

    // Database Configuration (Update these with actual credentials)
    private static final String DB_URL = "jdbc:mysql://localhost:3306/inventory_db";
    private static final String DB_USER = "db_user";
    private static final String DB_PASS = "secure_password";

    public static void main(String[] args) {
        // Optional: explicitly load driver (required for older JDBC versions)
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            System.err.println("MySQL JDBC Driver not found. Please add the mysql-connector-j jar to classpath.");
            return;
        }

        Scanner scanner = new Scanner(System.in);
        System.out.println("--- Product Inventory Search ---");

        try {
            // 1. Get and Validate Input
            System.out.print("Enter search keyword (product name or description): ");
            String keyword = scanner.nextLine().trim();

            if (keyword.isEmpty()) {
                System.out.println("Error: Search keyword cannot be empty.");
                return;
            }

            // 2. Perform Search
            searchProducts(keyword);

        } finally {
            scanner.close();
        }
    }

    /**
     * Executes the secure search query.
     */
    private static void searchProducts(String keyword) {
        // SQL Query using '?' placeholders.
        // We search both name and description fields using the LIKE operator.
        String sql = "SELECT id, name, description, price FROM products WHERE name LIKE ? OR description LIKE ?";

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            // Bind parameters. We add the wildcards '%' here in the Java code,
            // not in the SQL string, ensuring the database treats them as data.
            String searchPattern = "%" + keyword + "%";
            pstmt.setString(1, searchPattern);
            pstmt.setString(2, searchPattern);

            System.out.println("\nSearching for matches...");

            try (ResultSet rs = pstmt.executeQuery()) {
                printResults(rs);
            }

        } catch (SQLException e) {
            System.err.println("Database access error: " + e.getMessage());
        }
    }

    /**
     * Helper to format and display the result set.
     */
    private static void printResults(ResultSet rs) throws SQLException {
        boolean found = false;
        
        // Header
        System.out.printf("%-5s | %-20s | %-10s | %-30s%n", "ID", "Name", "Price", "Description");
        System.out.println("--------------------------------------------------------------------------");

        while (rs.next()) {
            found = true;
            int id = rs.getInt("id");
            String name = rs.getString("name");
            String desc = rs.getString("description");
            double price = rs.getDouble("price");

            // Truncate description if too long for the table view
            if (desc != null && desc.length() > 28) {
                desc = desc.substring(0, 25) + "...";
            }

            System.out.printf("%-5d | %-20s | $%-9.2f | %-30s%n", id, name, price, desc);
        }

        if (!found) {
            System.out.println("\nNo products found matching your keyword.");
        }
    }
}