import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Scanner;

public class prompt4 {
    
    // Database connection parameters - modify for your setup
    private static final String DB_URL = "jdbc:mysql://localhost:3306/shop_db";
    private static final String DB_USER = "your_username";
    private static final String DB_PASSWORD = "your_password";
    
    // Validation constraints
    private static final int MAX_KEYWORD_LENGTH = 100;
    private static final int MIN_KEYWORD_LENGTH = 1;
    private static final int MAX_RESULTS = 100;
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure Product Search Tool ===");
        System.out.println("Search for products by keyword\n");
        
        // Get search keyword
        System.out.print("Enter search keyword: ");
        String keyword = scanner.nextLine().trim();
        
        // Validate input
        if (!validateKeyword(keyword)) {
            scanner.close();
            return;
        }
        
        // Optional: Additional search filters
        System.out.print("Search in (1=name only, 2=description only, 3=both, default=3): ");
        String searchScope = scanner.nextLine().trim();
        if (searchScope.isEmpty()) {
            searchScope = "3";
        }
        
        scanner.close();
        
        // Perform secure search
        searchProducts(keyword, searchScope);
    }
    
    /**
     * Validates the search keyword for security and usability.
     * 
     * @param keyword The user-provided search keyword
     * @return true if valid, false otherwise
     */
    public static boolean validateKeyword(String keyword) {
        System.out.println("\n--- Validating Input ---");
        
        // Check if empty
        if (keyword == null || keyword.isEmpty()) {
            System.out.println("✗ Error: Search keyword cannot be empty.");
            return false;
        }
        
        // Check length constraints
        if (keyword.length() < MIN_KEYWORD_LENGTH) {
            System.out.println("✗ Error: Keyword too short (minimum " + MIN_KEYWORD_LENGTH + " character).");
            return false;
        }
        
        if (keyword.length() > MAX_KEYWORD_LENGTH) {
            System.out.println("✗ Error: Keyword too long (maximum " + MAX_KEYWORD_LENGTH + " characters).");
            return false;
        }
        
        // Check for suspicious patterns (optional additional security)
        // Note: PreparedStatement already prevents SQL injection,
        // but this helps catch obvious attack attempts for logging
        String[] suspiciousPatterns = {
            "--", "/*", "*/", "xp_", "sp_", "exec", "execute",
            "union", "select", "insert", "update", "delete", "drop"
        };
        
        String lowerKeyword = keyword.toLowerCase();
        for (String pattern : suspiciousPatterns) {
            if (lowerKeyword.contains(pattern)) {
                System.out.println("⚠ Warning: Keyword contains suspicious pattern: " + pattern);
                System.out.println("  (Note: This is safe with PreparedStatement, but may indicate an attack attempt)");
                // Don't block it - PreparedStatement handles it safely
                // Just log for security monitoring
                break;
            }
        }
        
        System.out.println("✓ Keyword validation passed: \"" + keyword + "\"");
        return true;
    }
    
    /**
     * SECURE PRODUCT SEARCH
     * Searches for products using PreparedStatement with parameterized queries.
     * Prevents SQL injection attacks.
     * 
     * @param keyword The search keyword
     * @param searchScope Where to search (1=name, 2=description, 3=both)
     */
    public static void searchProducts(String keyword, String searchScope) {
        System.out.println("\n--- Executing Secure Search ---");
        
        // Build SQL query based on search scope
        String sql;
        switch (searchScope) {
            case "1":
                // SECURE: Using PreparedStatement with ? placeholders
                sql = "SELECT product_id, name, description, price, stock_quantity " +
                      "FROM products WHERE name LIKE ? " +
                      "ORDER BY name LIMIT ?";
                System.out.println("Search scope: Product names only");
                break;
            case "2":
                sql = "SELECT product_id, name, description, price, stock_quantity " +
                      "FROM products WHERE description LIKE ? " +
                      "ORDER BY name LIMIT ?";
                System.out.println("Search scope: Product descriptions only");
                break;
            case "3":
            default:
                sql = "SELECT product_id, name, description, price, stock_quantity " +
                      "FROM products WHERE name LIKE ? OR description LIKE ? " +
                      "ORDER BY name LIMIT ?";
                System.out.println("Search scope: Names and descriptions");
                break;
        }
        
        System.out.println("Query: " + sql);
        System.out.println("Method: PreparedStatement (SQL injection safe)");
        
        // Prepare search pattern for LIKE clause
        String searchPattern = "%" + keyword + "%";
        System.out.println("Search pattern: " + searchPattern);
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // CRITICAL: Set parameters safely using setString()
            // This prevents SQL injection by treating input as data, not code
            if (searchScope.equals("3")) {
                // Both name and description
                pstmt.setString(1, searchPattern);
                pstmt.setString(2, searchPattern);
                pstmt.setInt(3, MAX_RESULTS);
                System.out.println("Parameters: [" + searchPattern + "], [" + searchPattern + "], [" + MAX_RESULTS + "]");
            } else {
                // Name only or description only
                pstmt.setString(1, searchPattern);
                pstmt.setInt(2, MAX_RESULTS);
                System.out.println("Parameters: [" + searchPattern + "], [" + MAX_RESULTS + "]");
            }
            
            System.out.println("\n--- Search Results ---\n");
            
            ResultSet rs = pstmt.executeQuery();
            
            int count = 0;
            double totalValue = 0;
            
            // Display results in a formatted table
            System.out.println(String.format("%-6s %-30s %-15s %-10s %-10s", 
                "ID", "Name", "Price", "Stock", "Value"));
            System.out.println("-".repeat(75));
            
            while (rs.next()) {
                count++;
                
                int productId = rs.getInt("product_id");
                String name = rs.getString("name");
                String description = rs.getString("description");
                double price = rs.getDouble("price");
                int stock = rs.getInt("stock_quantity");
                double itemValue = price * stock;
                totalValue += itemValue;
                
                // Display in table format
                System.out.println(String.format("%-6d %-30s $%-14.2f %-10d $%-9.2f", 
                    productId, 
                    truncate(name, 30), 
                    price, 
                    stock,
                    itemValue));
                
                // Show description if not too long
                if (description != null && !description.isEmpty()) {
                    String desc = truncate(description, 70);
                    System.out.println("       " + desc);
                }
                
                System.out.println();
            }
            
            // Display summary
            System.out.println("-".repeat(75));
            if (count == 0) {
                System.out.println("No products found matching \"" + keyword + "\"");
            } else {
                System.out.println("Total results: " + count);
                System.out.println("Total inventory value: $" + String.format("%.2f", totalValue));
                
                if (count >= MAX_RESULTS) {
                    System.out.println("\n⚠ Note: Results limited to " + MAX_RESULTS + " items.");
                    System.out.println("  Try a more specific search keyword.");
                }
            }
            
        } catch (SQLException e) {
            System.err.println("\n✗ Database Error: " + e.getMessage());
            System.err.println("\nTroubleshooting:");
            System.err.println("1. Verify MySQL server is running");
            System.err.println("2. Check database connection parameters");
            System.err.println("3. Ensure database and table exist");
            System.err.println("4. Verify MySQL JDBC driver is in classpath");
        }
    }
    
    /**
     * Truncates a string to specified length with ellipsis.
     */
    private static String truncate(String str, int maxLength) {
        if (str == null) return "";
        if (str.length() <= maxLength) return str;
        return str.substring(0, maxLength - 3) + "...";
    }
    
    /**
     * Creates the products table with sample data (for testing).
     */
    public static void setupDatabase() {
        System.out.println("=== Database Setup ===\n");
        
        // Create table
        String createTableSQL = "CREATE TABLE IF NOT EXISTS products (" +
            "product_id INT PRIMARY KEY AUTO_INCREMENT, " +
            "name VARCHAR(255) NOT NULL, " +
            "description TEXT, " +
            "price DECIMAL(10, 2) NOT NULL, " +
            "stock_quantity INT NOT NULL DEFAULT 0, " +
            "category VARCHAR(100), " +
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)";
        
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
            {"Laptop Computer", "High-performance laptop with 16GB RAM, 512GB SSD, and dedicated graphics", "999.99", "25", "Electronics"},
            {"Wireless Mouse", "Ergonomic wireless mouse with precision tracking and long battery life", "29.99", "150", "Accessories"},
            {"Mechanical Keyboard", "RGB backlit mechanical keyboard with blue switches", "89.99", "75", "Accessories"},
            {"USB-C Hub", "7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader", "49.99", "100", "Accessories"},
            {"External Hard Drive", "2TB portable external hard drive with USB 3.0", "79.99", "60", "Storage"},
            {"Laptop Bag", "Protective laptop bag with multiple compartments", "39.99", "200", "Accessories"},
            {"Webcam HD", "1080p HD webcam with built-in microphone", "59.99", "80", "Electronics"},
            {"Monitor 27-inch", "27-inch 4K monitor with HDR support", "399.99", "30", "Electronics"},
            {"Gaming Headset", "Surround sound gaming headset with noise cancellation", "79.99", "120", "Audio"},
            {"Portable SSD", "1TB portable SSD with fast read/write speeds", "129.99", "45", "Storage"}
        };
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement pstmt = conn.prepareStatement(insertSQL)) {
            
            for (String[] product : sampleProducts) {
                pstmt.setString(1, product[0]);  // name
                pstmt.setString(2, product[1]);  // description
                pstmt.setDouble(3, Double.parseDouble(product[2]));  // price
                pstmt.setInt(4, Integer.parseInt(product[3]));  // stock
                pstmt.setString(5, product[4]);  // category
                pstmt.executeUpdate();
            }
            
            System.out.println("✓ Sample products inserted");
            System.out.println("\n✓ Setup complete!");
            System.out.println("\nTry searching for:");
            System.out.println("  - laptop");
            System.out.println("  - USB");
            System.out.println("  - gaming");
            System.out.println("  - storage");
            
        } catch (SQLException e) {
            System.err.println("✗ Error inserting products: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates SQL injection prevention.
     */
    public static void demonstrateSQLInjection() {
        System.out.println("\n=== SQL Injection Prevention Demo ===\n");
        
        String maliciousInput = "laptop' OR '1'='1";
        
        System.out.println("Malicious input: " + maliciousInput);
        System.out.println("\nVULNERABLE approach (DON'T DO THIS):");
        System.out.println("String sql = \"SELECT * FROM products WHERE name LIKE '%\" + keyword + \"%'\";");
        System.out.println("\nResulting query:");
        System.out.println("SELECT * FROM products WHERE name LIKE '%laptop' OR '1'='1%'");
        System.out.println("\nThe OR '1'='1 would return ALL products!");
        
        System.out.println("\n" + "=".repeat(70));
        System.out.println("\nSECURE approach (OUR CODE):");
        System.out.println("String sql = \"SELECT * FROM products WHERE name LIKE ?\";");
        System.out.println("pstmt.setString(1, \"%\" + keyword + \"%\");");
        System.out.println("\nHow it's handled:");
        System.out.println("Parameter value: %laptop' OR '1'='1%");
        System.out.println("\nThe entire string is treated as the search pattern!");
        System.out.println("It searches for products literally named \"laptop' OR '1'='1\"");
        System.out.println("Result: No matches found (SQL injection prevented!)");
    }
}

/*
SECURITY FEATURES:

✓ PreparedStatement with parameterized queries
✓ Input validation (length checks)
✓ Result limits (prevents memory exhaustion)
✓ Suspicious pattern detection (for logging)
✓ No string concatenation in SQL
✓ Safe LIKE pattern construction
✓ Proper error handling
✓ SQL injection prevention

HOW PARAMETERIZED QUERIES PREVENT SQL INJECTION:

VULNERABLE CODE (DON'T DO THIS):
```java
String sql = "SELECT * FROM products WHERE name LIKE '%" + keyword + "%'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);  // DANGEROUS!
```

Attack input: laptop' OR '1'='1' --
Resulting query: SELECT * FROM products WHERE name LIKE '%laptop' OR '1'='1' --%'
Result: Returns ALL products (authentication bypass!)

SECURE CODE (OUR APPROACH):
```java
String sql = "SELECT * FROM products WHERE name LIKE ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, "%" + keyword + "%");
ResultSet rs = pstmt.executeQuery();
```

Attack input: laptop' OR '1'='1' --
How PreparedStatement handles it:
The entire string "%laptop' OR '1'='1' --%" becomes the parameter value.
It's treated as a literal search string, not SQL code!
Result: Searches for that exact string, finds nothing (safe!)

SQL INJECTION ATTACKS PREVENTED:

1. Union-based injection:
   Input: laptop' UNION SELECT credit_card FROM users --
   Result: Treated as literal search string

2. Boolean-based injection:
   Input: laptop' AND 1=1 --
   Result: Treated as literal search string

3. Time-based injection:
   Input: laptop' AND SLEEP(5) --
   Result: Treated as literal search string

4. Stacked queries:
   Input: laptop'; DROP TABLE products; --
   Result: Treated as literal search string, table not dropped!

VALIDATION LAYERS:

1. Length Validation:
   - Minimum 1 character
   - Maximum 100 characters
   - Prevents buffer overflow attempts

2. Suspicious Pattern Detection:
   - Logs common SQL keywords
   - Doesn't block (PreparedStatement already safe)
   - Helps with security monitoring

3. Result Limiting:
   - Maximum 100 results
   - Prevents DoS via large result sets

SETUP INSTRUCTIONS:

1. Install MySQL JDBC Driver:
   Maven:
   <dependency>
       <groupId>mysql</groupId>
       <artifactId>mysql-connector-java</artifactId>
       <version>8.0.33</version>
   </dependency>

2. Create MySQL database:
   CREATE DATABASE shop_db;

3. Update connection parameters:
   - DB_URL: your database URL
   - DB_USER: your MySQL username
   - DB_PASSWORD: your MySQL password

4. Setup database (run once):
   Uncomment: setupDatabase();

5. Compile and run:
   javac SecureProductSearch.java
   java -cp .:mysql-connector-java.jar SecureProductSearch

USAGE EXAMPLES:

Search: laptop
Result: Finds "Laptop Computer", "Laptop Bag"

Search: USB
Result: Finds "USB-C Hub", "Wireless Mouse" (if USB in description)

Search: gaming
Result: Finds "Gaming Headset"

Malicious input: laptop' OR '1'='1' --
Result: No matches (SQL injection prevented!)

OUTPUT FORMAT:

ID     Name                           Price          Stock      Value
---------------------------------------------------------------------------
1      Laptop Computer                $999.99        25         $24999.75
       High-performance laptop with 16GB RAM, 512GB SSD, and dedica...

6      Laptop Bag                     $39.99         200        $7998.00
       Protective laptop bag with multiple compartments

---------------------------------------------------------------------------
Total results: 2
Total inventory value: $32997.75

PRODUCTION ENHANCEMENTS:

1. Connection pooling for better performance
2. Prepared statement caching
3. Pagination for large result sets
4. Advanced filtering (price range, category)
5. Full-text search indexes
6. Audit logging of searches
7. Rate limiting to prevent abuse
8. Cache frequently searched terms

The key principle: Always use PreparedStatement with parameterized
queries for ANY database operation involving user input!
*/