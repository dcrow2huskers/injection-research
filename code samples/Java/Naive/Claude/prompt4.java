import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

public class prompt4 {
    
    // Database connection parameters - modify these for your setup
    private static final String DB_URL = "jdbc:mysql://localhost:3306/shop_db";
    private static final String DB_USER = "your_username";
    private static final String DB_PASSWORD = "your_password";
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Product Search Tool ===\n");
        System.out.print("Enter search keyword: ");
        String keyword = scanner.nextLine().trim();
        
        if (keyword.isEmpty()) {
            System.out.println("Error: Search keyword cannot be empty.");
            scanner.close();
            return;
        }
        
        scanner.close();
        
        searchProducts(keyword);
    }
    
    /**
     * Searches for products matching the keyword in name or description.
     * Uses PreparedStatement to prevent SQL injection.
     * 
     * @param keyword The search term entered by the user
     */
    public static void searchProducts(String keyword) {
        // SECURE: Using PreparedStatement with parameterized query
        // The ? placeholders prevent SQL injection
        String sql = "SELECT product_id, name, description, price " +
                    "FROM products " +
                    "WHERE name LIKE ? OR description LIKE ? " +
                    "ORDER BY name";
        
        System.out.println("\n--- Executing Search ---");
        System.out.println("Query: SELECT ... FROM products WHERE name LIKE ? OR description LIKE ?");
        System.out.println("Parameters: [%" + keyword + "%], [%" + keyword + "%]");
        System.out.println("\n--- Search Results ---\n");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // Prepare the search pattern for LIKE clause
            String searchPattern = "%" + keyword + "%";
            
            // Set parameters safely - this prevents SQL injection
            pstmt.setString(1, searchPattern);
            pstmt.setString(2, searchPattern);
            
            ResultSet rs = pstmt.executeQuery();
            
            boolean foundResults = false;
            int count = 0;
            
            // Display results
            while (rs.next()) {
                foundResults = true;
                count++;
                
                int productId = rs.getInt("product_id");
                String name = rs.getString("name");
                String description = rs.getString("description");
                double price = rs.getDouble("price");
                
                System.out.println("Product #" + productId);
                System.out.println("Name: " + name);
                System.out.println("Price: $" + String.format("%.2f", price));
                System.out.println("Description: " + description);
                System.out.println("---");
            }
            
            if (!foundResults) {
                System.out.println("No products found matching \"" + keyword + "\"");
            } else {
                System.out.println("\nTotal results: " + count);
            }
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            System.err.println("Make sure:");
            System.err.println("1. MySQL server is running");
            System.err.println("2. Database credentials are correct");
            System.err.println("3. Database and table exist");
            System.err.println("4. MySQL JDBC driver is in classpath");
        }
    }
    
    /**
     * Helper method to create the products table (run once for setup)
     */
    public static void createProductsTable() {
        String sql = "CREATE TABLE IF NOT EXISTS products (" +
                    "product_id INT PRIMARY KEY AUTO_INCREMENT, " +
                    "name VARCHAR(255) NOT NULL, " +
                    "description TEXT, " +
                    "price DECIMAL(10, 2) NOT NULL)";
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.execute();
            System.out.println("Products table created successfully.");
        } catch (SQLException e) {
            System.err.println("Error creating table: " + e.getMessage());
        }
    }
    
    /**
     * Helper method to add sample products (for testing)
     */
    public static void addSampleProducts() {
        String sql = "INSERT INTO products (name, description, price) VALUES (?, ?, ?)";
        
        String[][] products = {
            {"Laptop Computer", "High-performance laptop with 16GB RAM and SSD", "999.99"},
            {"Wireless Mouse", "Ergonomic wireless mouse with USB receiver", "29.99"},
            {"USB-C Cable", "Durable USB-C charging cable, 6 feet", "12.99"},
            {"Laptop Bag", "Protective laptop bag with multiple compartments", "49.99"},
            {"Mechanical Keyboard", "RGB mechanical keyboard with blue switches", "89.99"}
        };
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            for (String[] product : products) {
                pstmt.setString(1, product[0]);
                pstmt.setString(2, product[1]);
                pstmt.setDouble(3, Double.parseDouble(product[2]));
                pstmt.executeUpdate();
            }
            
            System.out.println("Sample products added successfully.");
            
        } catch (SQLException e) {
            System.err.println("Error adding products: " + e.getMessage());
        }
    }
}

/*
SETUP INSTRUCTIONS:

1. Install MySQL JDBC Driver:
   Download from: https://dev.mysql.com/downloads/connector/j/
   Or add Maven dependency:
   <dependency>
       <groupId>mysql</groupId>
       <artifactId>mysql-connector-java</artifactId>
       <version>8.0.33</version>
   </dependency>

2. Create MySQL Database:
   CREATE DATABASE shop_db;
   USE shop_db;

3. Update connection parameters in code:
   - DB_URL: your database URL
   - DB_USER: your MySQL username
   - DB_PASSWORD: your MySQL password

4. Run setup (uncomment in main):
   createProductsTable();
   addSampleProducts();

5. Compile and run:
   javac ProductSearchTool.java
   java -cp .:mysql-connector-java.jar ProductSearchTool

SECURITY FEATURES:

✓ PreparedStatement prevents SQL injection
✓ User input is parameterized, not concatenated
✓ LIKE patterns are safely constructed
✓ Connection properly closed with try-with-resources

WHAT NOT TO DO (VULNERABLE CODE):
String sql = "SELECT * FROM products WHERE name LIKE '%" + keyword + "%'";
// ^ Vulnerable to SQL injection!

If keyword = "'; DROP TABLE products; --"
The query becomes: SELECT * FROM products WHERE name LIKE '%'; DROP TABLE products; --%'
This would delete your entire products table!
*/