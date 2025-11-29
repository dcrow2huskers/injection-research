import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.util.Scanner;

public class prompt5 {
    
    // Database connection parameters - modify for your setup
    private static final String DB_URL = "jdbc:postgresql://localhost:5432/shop_db";
    private static final String DB_USER = "your_username";
    private static final String DB_PASSWORD = "your_password";
    
    // Validation constraints
    private static final int MIN_PRODUCT_NAME_LENGTH = 1;
    private static final int MAX_PRODUCT_NAME_LENGTH = 255;
    private static final int MIN_PRODUCT_ID = 1;
    private static final int MAX_PRODUCT_ID = 1000000;
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure Product Update Tool ===");
        System.out.println("Update product information safely\n");
        
        // Get product ID
        System.out.print("Enter Product ID: ");
        String productIdInput = scanner.nextLine().trim();
        
        // Validate product ID
        int productId;
        if (!validateProductId(productIdInput)) {
            scanner.close();
            return;
        }
        productId = Integer.parseInt(productIdInput);
        
        // Get new product name
        System.out.print("Enter new product name: ");
        String newName = scanner.nextLine().trim();
        
        // Validate product name
        if (!validateProductName(newName)) {
            scanner.close();
            return;
        }
        
        scanner.close();
        
        // Show current product info before updating
        System.out.println("\n--- Current Product Information ---");
        ProductInfo currentInfo = getProductInfo(productId);
        
        if (currentInfo == null) {
            System.out.println("✗ Product ID " + productId + " not found.");
            System.out.println("Update cancelled.");
            return;
        }
        
        displayProductInfo(currentInfo);
        
        // Perform the secure update
        int rowsUpdated = updateProductName(productId, newName);
        
        // Show updated product info
        if (rowsUpdated > 0) {
            System.out.println("\n--- Updated Product Information ---");
            ProductInfo updatedInfo = getProductInfo(productId);
            if (updatedInfo != null) {
                displayProductInfo(updatedInfo);
            }
        }
    }
    
    /**
     * Validates product ID input.
     * 
     * @param productIdInput The user-provided product ID string
     * @return true if valid, false otherwise
     */
    public static boolean validateProductId(String productIdInput) {
        System.out.println("\n--- Validating Product ID ---");
        
        // Check if empty
        if (productIdInput == null || productIdInput.isEmpty()) {
            System.out.println("✗ Error: Product ID cannot be empty.");
            return false;
        }
        
        // Check if numeric
        try {
            int productId = Integer.parseInt(productIdInput);
            
            // Check range
            if (productId < MIN_PRODUCT_ID || productId > MAX_PRODUCT_ID) {
                System.out.println("✗ Error: Product ID must be between " + 
                    MIN_PRODUCT_ID + " and " + MAX_PRODUCT_ID + ".");
                return false;
            }
            
            System.out.println("✓ Product ID validation passed: " + productId);
            return true;
            
        } catch (NumberFormatException e) {
            System.out.println("✗ Error: Product ID must be a valid integer.");
            return false;
        }
    }
    
    /**
     * Validates product name input.
     * 
     * @param productName The user-provided product name
     * @return true if valid, false otherwise
     */
    public static boolean validateProductName(String productName) {
        System.out.println("\n--- Validating Product Name ---");
        
        // Check if empty
        if (productName == null || productName.isEmpty()) {
            System.out.println("✗ Error: Product name cannot be empty.");
            return false;
        }
        
        // Check length
        if (productName.length() < MIN_PRODUCT_NAME_LENGTH) {
            System.out.println("✗ Error: Product name too short (minimum " + 
                MIN_PRODUCT_NAME_LENGTH + " character).");
            return false;
        }
        
        if (productName.length() > MAX_PRODUCT_NAME_LENGTH) {
            System.out.println("✗ Error: Product name too long (maximum " + 
                MAX_PRODUCT_NAME_LENGTH + " characters).");
            return false;
        }
        
        // Check for only whitespace
        if (productName.trim().isEmpty()) {
            System.out.println("✗ Error: Product name cannot be only whitespace.");
            return false;
        }
        
        // Optional: Check for suspicious SQL keywords (for logging/monitoring)
        // Note: PreparedStatement makes this safe anyway
        String[] suspiciousPatterns = {"--", "/*", "*/", ";", "drop", "delete", "truncate"};
        String lowerName = productName.toLowerCase();
        
        for (String pattern : suspiciousPatterns) {
            if (lowerName.contains(pattern)) {
                System.out.println("⚠ Warning: Product name contains suspicious pattern: " + pattern);
                System.out.println("  (Note: This is safe with PreparedStatement)");
                break;
            }
        }
        
        System.out.println("✓ Product name validation passed: \"" + productName + "\"");
        return true;
    }
    
    /**
     * SECURE PRODUCT UPDATE
     * Updates product name using PreparedStatement with parameterized query.
     * Prevents SQL injection attacks.
     * 
     * @param productId The ID of the product to update
     * @param newName The new name for the product
     * @return Number of rows updated (should be 0 or 1)
     */
    public static int updateProductName(int productId, String newName) {
        System.out.println("\n--- Executing Secure Update ---");
        
        // SECURE: Using PreparedStatement with ? placeholders
        // This prevents SQL injection by treating input as data, not SQL code
        String sql = "UPDATE products SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?";
        
        System.out.println("Query: UPDATE products SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?");
        System.out.println("Parameters: [" + newName + "], [" + productId + "]");
        System.out.println("Method: PreparedStatement (SQL injection safe)");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // CRITICAL: Set parameters safely using setString() and setInt()
            // This prevents SQL injection
            pstmt.setString(1, newName);     // New product name
            pstmt.setInt(2, productId);       // Product ID for WHERE clause
            
            // Execute the update and get the number of affected rows
            int rowsUpdated = pstmt.executeUpdate();
            
            System.out.println("\n--- Update Result ---");
            System.out.println("Rows updated: " + rowsUpdated);
            
            if (rowsUpdated == 0) {
                System.out.println("⚠ Warning: No product found with ID " + productId);
                System.out.println("  The product may have been deleted or the ID is incorrect.");
            } else if (rowsUpdated == 1) {
                System.out.println("✓ Product updated successfully!");
            } else {
                // This should never happen with proper primary key constraint
                System.out.println("⚠ Warning: Multiple rows were updated (" + rowsUpdated + ")");
                System.out.println("  This indicates a database integrity issue.");
            }
            
            return rowsUpdated;
            
        } catch (SQLException e) {
            System.err.println("\n✗ Database Error: " + e.getMessage());
            System.err.println("\nTroubleshooting:");
            System.err.println("1. Verify PostgreSQL server is running");
            System.err.println("2. Check database connection parameters");
            System.err.println("3. Ensure database and table exist");
            System.err.println("4. Verify PostgreSQL JDBC driver is in classpath");
            System.err.println("5. Check user permissions for UPDATE operation");
            return -1;
        }
    }
    
    /**
     * Retrieves current product information.
     * Uses PreparedStatement for security.
     * 
     * @param productId The product ID to retrieve
     * @return ProductInfo object or null if not found
     */
    public static ProductInfo getProductInfo(int productId) {
        // SECURE: Using PreparedStatement
        String sql = "SELECT product_id, name, description, price, stock_quantity, category, " +
                    "created_at, updated_at FROM products WHERE product_id = ?";
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, productId);
            ResultSet rs = pstmt.executeQuery();
            
            if (rs.next()) {
                ProductInfo info = new ProductInfo();
                info.productId = rs.getInt("product_id");
                info.name = rs.getString("name");
                info.description = rs.getString("description");
                info.price = rs.getDouble("price");
                info.stockQuantity = rs.getInt("stock_quantity");
                info.category = rs.getString("category");
                info.createdAt = rs.getTimestamp("created_at");
                info.updatedAt = rs.getTimestamp("updated_at");
                return info;
            }
            
            return null;
            
        } catch (SQLException e) {
            System.err.println("Error retrieving product info: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Displays product information in a formatted way.
     */
    private static void displayProductInfo(ProductInfo info) {
        System.out.println("Product ID:    " + info.productId);
        System.out.println("Name:          " + info.name);
        System.out.println("Description:   " + (info.description != null ? info.description : "N/A"));
        System.out.println("Price:         $" + String.format("%.2f", info.price));
        System.out.println("Stock:         " + info.stockQuantity);
        System.out.println("Category:      " + (info.category != null ? info.category : "N/A"));
        System.out.println("Created:       " + info.createdAt);
        System.out.println("Last Updated:  " + info.updatedAt);
    }
    
    /**
     * Class to hold product information.
     */
    private static class ProductInfo {
        int productId;
        String name;
        String description;
        double price;
        int stockQuantity;
        String category;
        Timestamp createdAt;
        Timestamp updatedAt;
    }
    
    /**
     * Sets up the database with table and sample data (for testing).
     */
    public static void setupDatabase() {
        System.out.println("=== Database Setup ===\n");
        
        // Create products table
        String createTableSQL = "CREATE TABLE IF NOT EXISTS products (" +
            "product_id SERIAL PRIMARY KEY, " +
            "name VARCHAR(255) NOT NULL, " +
            "description TEXT, " +
            "price NUMERIC(10, 2) NOT NULL, " +
            "stock_quantity INTEGER NOT NULL DEFAULT 0, " +
            "category VARCHAR(100), " +
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)";
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             Statement stmt = conn.createStatement()) {
            
            stmt.execute(createTableSQL);
            System.out.println("✓ Products table created");
            
        } catch (SQLException e) {
            System.err.println("✗ Error creating table: " + e.getMessage());
            return;
        }
        
        // Insert sample products using PreparedStatement
        String insertSQL = "INSERT INTO products (name, description, price, stock_quantity, category) " +
                          "VALUES (?, ?, ?, ?, ?)";
        
        String[][] sampleProducts = {
            {"Laptop", "High-performance laptop", "999.99", "25", "Electronics"},
            {"Mouse", "Wireless ergonomic mouse", "29.99", "150", "Accessories"},
            {"Keyboard", "Mechanical keyboard", "89.99", "75", "Accessories"},
            {"Monitor", "27-inch 4K display", "399.99", "30", "Electronics"},
            {"Headset", "Gaming headset", "79.99", "120", "Audio"}
        };
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(insertSQL)) {
            
            for (String[] product : sampleProducts) {
                pstmt.setString(1, product[0]);
                pstmt.setString(2, product[1]);
                pstmt.setDouble(3, Double.parseDouble(product[2]));
                pstmt.setInt(4, Integer.parseInt(product[3]));
                pstmt.setString(5, product[4]);
                pstmt.executeUpdate();
            }
            
            System.out.println("✓ Sample products inserted");
            System.out.println("\n✓ Setup complete!");
            System.out.println("\nYou can now update products by ID (1-5)");
            
        } catch (SQLException e) {
            System.err.println("✗ Error inserting products: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates SQL injection prevention.
     */
    public static void demonstrateSQLInjection() {
        System.out.println("\n=== SQL Injection Prevention Demo ===\n");
        
        String maliciousName = "Laptop', price = 0.01 WHERE product_id > 0; --";
        int productId = 1;
        
        System.out.println("Malicious product name: " + maliciousName);
        System.out.println("Product ID: " + productId);
        
        System.out.println("\nVULNERABLE approach (DON'T DO THIS):");
        System.out.println("String sql = \"UPDATE products SET name = '\" + name + \"' WHERE product_id = \" + id;");
        
        System.out.println("\nResulting query:");
        System.out.println("UPDATE products SET name = 'Laptop', price = 0.01 WHERE product_id > 0; --' WHERE product_id = 1");
        
        System.out.println("\nWhat happens:");
        System.out.println("1. Sets name to 'Laptop'");
        System.out.println("2. Sets price to $0.01 for ALL products (product_id > 0)");
        System.out.println("3. Comments out the original WHERE clause");
        System.out.println("Result: ALL products now cost $0.01! Massive financial loss!");
        
        System.out.println("\n" + "=".repeat(70));
        System.out.println("\nSECURE approach (OUR CODE):");
        System.out.println("String sql = \"UPDATE products SET name = ? WHERE product_id = ?\";");
        System.out.println("pstmt.setString(1, name);");
        System.out.println("pstmt.setInt(2, id);");
        
        System.out.println("\nHow PreparedStatement handles it:");
        System.out.println("Parameter 1: Laptop', price = 0.01 WHERE product_id > 0; --");
        System.out.println("Parameter 2: 1");
        
        System.out.println("\nWhat happens:");
        System.out.println("The entire malicious string becomes the product name!");
        System.out.println("Only product ID 1 is updated with that weird name.");
        System.out.println("No price changes, no other products affected.");
        System.out.println("Result: SQL injection prevented! ✓");
    }
    
    /**
     * Batch update example (updates multiple products safely).
     */
    public static void batchUpdateExample() {
        System.out.println("\n=== Batch Update Example ===\n");
        
        String sql = "UPDATE products SET price = price * ? WHERE category = ?";
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // 10% discount on Electronics
            pstmt.setDouble(1, 0.9);
            pstmt.setString(2, "Electronics");
            int updated = pstmt.executeUpdate();
            
            System.out.println("✓ Applied 10% discount to " + updated + " Electronics products");
            
        } catch (SQLException e) {
            System.err.println("Error in batch update: " + e.getMessage());
        }
    }
}

/*
SECURITY FEATURES:

✓ PreparedStatement with parameterized queries
✓ Comprehensive input validation
✓ Type-safe parameter binding
✓ No string concatenation in SQL
✓ Before/after comparison
✓ Proper error handling
✓ Row count verification
✓ SQL injection prevention

HOW PARAMETERIZED UPDATES PREVENT SQL INJECTION:

VULNERABLE CODE (DON'T DO THIS):
```java
String sql = "UPDATE products SET name = '" + newName + 
             "' WHERE product_id = " + productId;
Statement stmt = conn.createStatement();
int rows = stmt.executeUpdate(sql);  // DANGEROUS!
```

Attack input:
Product ID: 1
New name: Laptop', price = 0.01 WHERE product_id > 0; --

Resulting query:
UPDATE products SET name = 'Laptop', price = 0.01 WHERE product_id > 0; --' WHERE product_id = 1

What happens:
1. Sets name to 'Laptop'
2. Sets price to $0.01 for ALL products
3. Comments out the intended WHERE clause
Result: ALL products now cost $0.01! Financial catastrophe!

SECURE CODE (OUR APPROACH):
```java
String sql = "UPDATE products SET name = ? WHERE product_id = ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, newName);
pstmt.setInt(2, productId);
int rows = pstmt.executeUpdate();
```

Same attack input:
PreparedStatement treats the entire string as the name value:
"Laptop', price = 0.01 WHERE product_id > 0; --"

Result:
Only product ID 1 gets updated with that literal string as its name.
No SQL injection, no price changes to other products!

SQL INJECTION ATTACKS PREVENTED:

1. Price Manipulation:
   Input: Laptop', price = 0 --
   Result: Treated as literal product name

2. Mass Updates:
   Input: X' WHERE 1=1; --
   Result: Treated as literal product name

3. Data Deletion:
   Input: X'; DELETE FROM products; --
   Result: Treated as literal product name, no deletion

4. Privilege Escalation:
   Input: X'; UPDATE users SET role='admin'; --
   Result: Treated as literal product name

VALIDATION FEATURES:

1. Product ID Validation:
   ✓ Must be numeric
   ✓ Range check (1 to 1,000,000)
   ✓ Type-safe integer parsing

2. Product Name Validation:
   ✓ Non-empty check
   ✓ Length constraints (1-255 chars)
   ✓ Whitespace-only rejection
   ✓ Suspicious pattern detection

3. Update Verification:
   ✓ Shows current state before update
   ✓ Reports rows affected
   ✓ Shows updated state after update
   ✓ Warns if no rows updated

SETUP INSTRUCTIONS:

1. Install PostgreSQL JDBC Driver:
   Maven:
   <dependency>
       <groupId>org.postgresql</groupId>
       <artifactId>postgresql</artifactId>
       <version>42.6.0</version>
   </dependency>

2. Create PostgreSQL database:
   CREATE DATABASE shop_db;

3. Update connection parameters:
   - DB_URL: your database URL
   - DB_USER: your PostgreSQL username
   - DB_PASSWORD: your PostgreSQL password

4. Setup database (run once):
   Uncomment: setupDatabase();

5. Compile and run:
   javac SecureProductUpdater.java
   java -cp .:postgresql.jar SecureProductUpdater

USAGE EXAMPLE:

=== Secure Product Update Tool ===

Enter Product ID: 1

--- Validating Product ID ---
✓ Product ID validation passed: 1

Enter new product name: Gaming Laptop

--- Validating Product Name ---
✓ Product name validation passed: "Gaming Laptop"

--- Current Product Information ---
Product ID:    1
Name:          Laptop
Price:         $999.99
Stock:         25
Created:       2024-01-15 10:30:00
Last Updated:  2024-01-15 10:30:00

--- Executing Secure Update ---
Query: UPDATE products SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?
Parameters: [Gaming Laptop], [1]
Method: PreparedStatement (SQL injection safe)

--- Update Result ---
Rows updated: 1
✓ Product updated successfully!

--- Updated Product Information ---
Product ID:    1
Name:          Gaming Laptop
Price:         $999.99
Stock:         25
Created:       2024-01-15 10:30:00
Last Updated:  2024-11-29 14:45:23

PRODUCTION ENHANCEMENTS:

1. Transaction support for complex updates
2. Optimistic locking (version numbers)
3. Audit trail logging
4. Change history tracking
5. Role-based access control
6. Concurrent update detection
7. Rollback capabilities
8. Notification system for changes

The fundamental principle: Always use PreparedStatement with
parameterized queries for ANY database modification!
*/