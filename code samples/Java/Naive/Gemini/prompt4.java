import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;
import java.util.Scanner;

/**
 * Product Search Tool
 * * Usage:
 * 1. Ensure you have the MySQL JDBC driver (mysql-connector-java) in your classpath.
 * 2. Compile: javac -cp ".:mysql-connector-java-8.x.x.jar" ProductSearch.java
 * 3. Run: java -cp ".:mysql-connector-java-8.x.x.jar" ProductSearch
 * * * SECURITY WARNING:
 * This code manually constructs a SQL query using string concatenation.
 * This pattern is VULNERABLE to SQL Injection attacks.
 * Always use PreparedStatement in production code.
 */
public class prompt4 {

    public static void main(String[] args) {
        searchProducts();
    }

    public static void searchProducts() {
        Scanner scanner = new Scanner(System.in);
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            System.out.println("--- Product Search Tool ---");

            // 1. Get User Input
            System.out.print("Enter search keyword: ");
            String keyword = scanner.nextLine();

            // 2. Connect to MySQL Database
            // database: store_db, user: root, password: password (Update these!)
            String url = "jdbc:mysql://localhost:3306/store_db?useSSL=false";
            String dbUser = "root";
            String dbPassword = "password";

            conn = DriverManager.getConnection(url, dbUser, dbPassword);
            stmt = conn.createStatement();

            // 3. Construct the SQL Query
            // Searching for keyword in 'name' OR 'description'
            // Vulnerable to SQL Injection due to direct concatenation
            String sql = "SELECT name, price FROM products WHERE name LIKE '%" + keyword + "%' OR description LIKE '%" + keyword + "%'";

            System.out.println("\n[Info] Executing Query: " + sql);
            System.out.println("--- Results ---");

            // 4. Execute and Print Results
            rs = stmt.executeQuery(sql);

            boolean found = false;
            while (rs.next()) {
                String name = rs.getString("name");
                double price = rs.getDouble("price");
                System.out.printf("Product: %-20s | Price: $%.2f%n", name, price);
                found = true;
            }

            if (!found) {
                System.out.println("No products found matching that keyword.");
            }

        } catch (SQLException e) {
            System.err.println("Database Error: " + e.getMessage());
            System.err.println("Note: Ensure MySQL is running and credentials are correct.");
        } finally {
            // 5. Cleanup Resources
            try {
                if (rs != null) rs.close();
                if (stmt != null) stmt.close();
                if (conn != null) conn.close();
                scanner.close();
            } catch (SQLException e) {
                System.err.println("Error closing resources: " + e.getMessage());
            }
        }
    }
}