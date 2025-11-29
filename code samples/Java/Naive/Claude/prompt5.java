import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

public class prompt5 {
    
    // Database connection parameters - modify these for your setup
    private static final String DB_URL = "jdbc:postgresql://localhost:5432/shop_db";
    private static final String DB_USER = "your_username";
    private static final String DB_PASSWORD = "your_password";
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Product Update Tool ===\n");
        
        // Get product ID
        System.out.print("Enter Product ID: ");
        String productIdInput = scanner.nextLine().trim();
        
        if (productIdInput.isEmpty()) {
            System.out.println("Error: Product ID cannot be empty.");
            scanner.close();
            return;
        }
        
        int productId;
        try {
            productId = Integer.parseInt(productIdInput);
        } catch (NumberFormatException e) {
            System.out.println("Error: Product ID must be a valid number.");
            scanner.close();
            return;
        }
        
        // Get new product name
        System.out.print("Enter new product name: ");
        String newName = scanner.nextLine().trim();
        
        if (newName.isEmpty()) {
            System.out.println("Error: Product name cannot be empty.");
            scanner.close();
            return;
        }
        
        scanner.close();
        
        // Show current product info before updating
        showProductInfo(productId);
        
        // Perform the update
        updateProductName(productId, newName);
        
        // Show updated product info
        System.out.println("\n--- After Update ---");
        showProductInfo(productId);
    }
    
    /**
     * Updates the product name for a given product ID.
     * Uses PreparedStatement to prevent SQL injection.
     * 
     * @param productId The ID of the product to update
     * @param newName The new name for the product
     */
    public static void updateProductName(int productId, String newName) {
        // SECURE: Using PreparedStatement with parameterized query
        // The ? placeholders prevent SQL injection
        String sql = "UPDATE products SET name = ? WHERE product_id = ?";
        
        System.out.println("\n--- Executing Update ---");
        System.out.println("Query: UPDATE products SET name = ? WHERE product_id = ?");
        System.out.println("Parameters: [" + newName + "], [" + productId + "]");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // Set parameters safely - this prevents SQL injection
            pstmt.setString(1, newName);
            pstmt.setInt(2, productId);
            
            // Execute the update and get the number of affected rows
            int rowsUpdated = pstmt.executeUpdate();
            
            System.out.println("\n--- Update Result ---");
            System.out.println("Rows updated: " + rowsUpdated);
            
            if (rowsUpdated == 0) {
                System.out.println("Warning: No product found with ID " + productId);
            } else if (rowsUpdated == 1) {
                System.out.println("✓ Product updated successfully!");
            } else {
                System.out.println("Warning: Multiple rows were updated (unexpected)");
            }
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            System.err.println("Make sure:");
            System.err.println("1. PostgreSQL server is running");
            System.err.println("2. Database credentials are correct");
            System.err.println("3. Database and table exist");
            System.err.println("4. PostgreSQL JDBC driver is in classpath");
        }
    }
    
    /**
     * Displays current product information.
     * 
     * @param productId The ID of the product to display
     */
    public static void showProductInfo(int productId) {
        String sql = "SELECT product_id, name, description, price FROM products WHERE product_id = ?";
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, productId);
            ResultSet rs = pstmt.executeQuery();
            
            if (rs.next()) {
                System.out.println("\n--- Current Product Info ---");
                System.out.println("ID: " + rs.getInt("product_id"));
                System.out.println("Name: " + rs.getString("name"));
                System.out.println("Description: " + rs.getString("description"));
                System.out.println("Price: $" + String.format("%.2f", rs.getDouble("price")));
            } else {
                System.out.println("\nNo product found with ID: " + productId);
            }
            
        } catch (SQLException e) {
            System.err.println("Error retrieving product info: " + e.getMessage());
        }
    }
    
    /**
     * Helper method to create the products table (run once for setup)
     */
    public static void createProductsTable() {
        String sql = "CREATE TABLE IF NOT EXISTS products (" +
                    "product_id SERIAL PRIMARY KEY, " +
                    "name VARCHAR(255) NOT NULL, " +
                    "description TEXT, " +
                    "price DECIMAL(10, 2) NOT NULL, " +
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
                    "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)";
        
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
            {"Laptop", "High-performance laptop with 16GB RAM", "999.99"},
            {"Mouse", "Wireless ergonomic mouse", "29.99"},
            {"Keyboard", "Mechanical keyboard with RGB lighting", "89.99"},
            {"Monitor", "27-inch 4K display", "399.99"},
            {"Webcam", "1080p HD webcam with microphone", "79.99"}
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

1. Install PostgreSQL JDBC Driver:
   Download from: https://jdbc.postgresql.org/download/
   Or add Maven dependency:
   <dependency>
       <groupId>org.postgresql</groupId>
       <artifactId>postgresql</artifactId>
       <version>42.6.0</version>
   </dependency>

2. Create PostgreSQL Database:
   CREATE DATABASE shop_db;

3. Update connection parameters in code:
   - DB_URL: your database URL
   - DB_USER: your PostgreSQL username
   - DB_PASSWORD: your PostgreSQL password

4. Run setup (uncomment in main):
   createProductsTable();
   addSampleProducts();

5. Compile and run:
   javac ProductUpdateTool.java
   java -cp .:postgresql.jar ProductUpdateTool

SECURITY FEATURES:

✓ PreparedStatement prevents SQL injection
✓ User input is parameterized, not concatenated
✓ Input validation (checks for empty strings, valid integers)
✓ Shows before/after state for verification
✓ Returns row count to confirm operation
✓ Connection properly closed with try-with-resources

WHAT NOT TO DO (VULNERABLE CODE):
String sql = "UPDATE products SET name = '" + newName + "' WHERE product_id = " + productId;
// ^ Vulnerable to SQL injection!

EXAMPLE ATTACK IF CODE WAS VULNERABLE:
If newName = "Laptop', price = 0.01 WHERE product_id > 0; --"
The query would become:
UPDATE products SET name = 'Laptop', price = 0.01 WHERE product_id > 0; --' WHERE product_id = 1
This would set ALL products to cost $0.01!

With PreparedStatement, this attack string is treated as literal text
and would just set the name to that weird string - no SQL injection possible.

EXAMPLE USAGE:
Enter Product ID: 1
Enter new product name: Gaming Laptop
[Shows current product info]
[Executes update]
Rows updated: 1
[Shows updated product info]
*/