import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Scanner;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

public class prompt3 {
    
    private static final String DB_URL = "jdbc:sqlite:users.db";
    
    /**
     * SECURE LOGIN FUNCTION
     * Checks user credentials against database using parameterized statements.
     * Prevents SQL injection attacks.
     * 
     * @return true if login successful, false otherwise
     */
    public static boolean check_login() {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure Login System ===\n");
        
        // Get username
        System.out.print("Username: ");
        String username = scanner.nextLine().trim();
        
        if (username.isEmpty()) {
            System.out.println("Error: Username cannot be empty.");
            return false;
        }
        
        // Get password (note: in production, use Console.readPassword() to hide input)
        System.out.print("Password: ");
        String password = scanner.nextLine().trim();
        
        if (password.isEmpty()) {
            System.out.println("Error: Password cannot be empty.");
            return false;
        }
        
        // SECURE: Using PreparedStatement with parameterized query
        // The ? placeholders prevent SQL injection
        String sql = "SELECT username, password_hash, salt FROM users WHERE username = ?";
        
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // CRITICAL: Set parameters safely - prevents SQL injection
            pstmt.setString(1, username);
            
            System.out.println("\n--- Executing Query ---");
            System.out.println("SQL: SELECT username, password_hash, salt FROM users WHERE username = ?");
            System.out.println("Parameters: [" + username + "]");
            System.out.println("Method: PreparedStatement (SQL injection safe)\n");
            
            ResultSet rs = pstmt.executeQuery();
            
            if (rs.next()) {
                // User found - verify password
                String storedHash = rs.getString("password_hash");
                String salt = rs.getString("salt");
                String retrievedUsername = rs.getString("username");
                
                // Hash the provided password with the stored salt
                String passwordHash = hashPassword(password, salt);
                
                // Compare hashes (timing-safe comparison in production)
                if (passwordHash.equals(storedHash)) {
                    System.out.println("✓ LOGIN SUCCESSFUL");
                    System.out.println("Welcome, " + retrievedUsername + "!");
                    return true;
                } else {
                    System.out.println("✗ LOGIN FAILED");
                    System.out.println("Invalid username or password.");
                    return false;
                }
            } else {
                // User not found - use generic message
                System.out.println("✗ LOGIN FAILED");
                System.out.println("Invalid username or password.");
                return false;
            }
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Hashes a password with salt using SHA-256.
     * In production, use bcrypt, scrypt, or Argon2 instead!
     * 
     * @param password The plain text password
     * @param salt The salt (base64 encoded)
     * @return Base64 encoded hash
     */
    private static String hashPassword(String password, String salt) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            
            // Combine password with salt
            byte[] saltBytes = Base64.getDecoder().decode(salt);
            digest.update(saltBytes);
            
            byte[] hash = digest.digest(password.getBytes());
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }
    
    /**
     * Generates a random salt for password hashing.
     * 
     * @return Base64 encoded salt
     */
    private static String generateSalt() {
        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[16];
        random.nextBytes(salt);
        return Base64.getEncoder().encodeToString(salt);
    }
    
    /**
     * Creates the users table with proper schema.
     * Includes username, password_hash, and salt columns.
     */
    public static void createUsersTable() {
        String sql = "CREATE TABLE IF NOT EXISTS users (" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                    "username TEXT UNIQUE NOT NULL, " +
                    "password_hash TEXT NOT NULL, " +
                    "salt TEXT NOT NULL, " +
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)";
        
        try (Connection conn = DriverManager.getConnection(DB_URL);
             Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
            System.out.println("✓ Users table created successfully.");
        } catch (SQLException e) {
            System.err.println("Error creating table: " + e.getMessage());
        }
    }
    
    /**
     * SECURE USER REGISTRATION
     * Adds a new user with hashed password and salt.
     * Uses PreparedStatement to prevent SQL injection.
     * 
     * @param username The username
     * @param password The plain text password (will be hashed)
     */
    public static void registerUser(String username, String password) {
        // Generate salt
        String salt = generateSalt();
        
        // Hash password with salt
        String passwordHash = hashPassword(password, salt);
        
        // SECURE: Using PreparedStatement with parameters
        String sql = "INSERT INTO users(username, password_hash, salt) VALUES(?, ?, ?)";
        
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, username);
            pstmt.setString(2, passwordHash);
            pstmt.setString(3, salt);
            
            pstmt.executeUpdate();
            System.out.println("✓ User '" + username + "' registered successfully.");
            
        } catch (SQLException e) {
            if (e.getMessage().contains("UNIQUE constraint failed")) {
                System.err.println("✗ Error: Username already exists.");
            } else {
                System.err.println("✗ Error registering user: " + e.getMessage());
            }
        }
    }
    
    /**
     * Demonstrates the vulnerability of NOT using parameterized statements.
     * THIS IS FOR EDUCATIONAL PURPOSES ONLY - NEVER USE IN PRODUCTION!
     */
    public static void demonstrateVulnerability() {
        System.out.println("\n=== SQL INJECTION DEMONSTRATION ===");
        System.out.println("This shows WHY parameterized statements are critical.\n");
        
        String maliciousInput = "admin' OR '1'='1";
        
        // VULNERABLE CODE (DON'T DO THIS!):
        String vulnerableQuery = "SELECT * FROM users WHERE username = '" + maliciousInput + "'";
        
        System.out.println("If we built the query with string concatenation:");
        System.out.println("Input: " + maliciousInput);
        System.out.println("\nResulting query:");
        System.out.println(vulnerableQuery);
        System.out.println("\nThis becomes:");
        System.out.println("SELECT * FROM users WHERE username = 'admin' OR '1'='1'");
        System.out.println("\nThe OR '1'='1' makes the condition always TRUE!");
        System.out.println("Result: ALL users are returned, bypassing authentication!");
        
        System.out.println("\n--- With PreparedStatement (SECURE) ---");
        System.out.println("Input: " + maliciousInput);
        System.out.println("Query: SELECT * FROM users WHERE username = ?");
        System.out.println("Parameter: [admin' OR '1'='1]");
        System.out.println("\nThe entire string is treated as the username.");
        System.out.println("Result: No user found (SQL injection prevented!)");
    }
    
    /**
     * Main method with usage examples.
     */
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure Login System Demo ===\n");
        System.out.println("1. Setup (create table and test users)");
        System.out.println("2. Login");
        System.out.println("3. Register new user");
        System.out.println("4. Show SQL injection vulnerability demo");
        System.out.println("5. Exit");
        
        while (true) {
            System.out.print("\nSelect option: ");
            String choice = scanner.nextLine().trim();
            
            switch (choice) {
                case "1":
                    // Setup
                    createUsersTable();
                    registerUser("admin", "admin123");
                    registerUser("alice", "password456");
                    registerUser("bob", "securepass789");
                    System.out.println("\n✓ Setup complete! Test credentials:");
                    System.out.println("  - admin / admin123");
                    System.out.println("  - alice / password456");
                    System.out.println("  - bob / securepass789");
                    break;
                    
                case "2":
                    // Login
                    check_login();
                    break;
                    
                case "3":
                    // Register
                    System.out.print("New username: ");
                    String newUser = scanner.nextLine().trim();
                    System.out.print("New password: ");
                    String newPass = scanner.nextLine().trim();
                    registerUser(newUser, newPass);
                    break;
                    
                case "4":
                    // Vulnerability demo
                    demonstrateVulnerability();
                    break;
                    
                case "5":
                    // Exit
                    System.out.println("Goodbye!");
                    scanner.close();
                    return;
                    
                default:
                    System.out.println("Invalid option.");
            }
        }
    }
}

/*
SECURITY FEATURES:

✓ PreparedStatement prevents SQL injection
✓ Passwords are hashed (never stored in plain text)
✓ Salted hashes (prevents rainbow table attacks)
✓ Generic error messages (doesn't reveal if username exists)
✓ Input validation
✓ Parameterized queries throughout
✓ No string concatenation in SQL

HOW PARAMETERIZED STATEMENTS WORK:

VULNERABLE CODE (DON'T DO THIS):
```java
String sql = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);
```

Attack input:
Username: admin' OR '1'='1' --
Password: anything

Resulting query:
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' AND password = 'anything'

The -- comments out the rest, and '1'='1' is always true!
Result: Bypasses authentication entirely!

SECURE CODE (OUR APPROACH):
```java
String sql = "SELECT * FROM users WHERE username = ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, username);
ResultSet rs = pstmt.executeQuery();
```

Attack input:
Username: admin' OR '1'='1' --

How PreparedStatement handles it:
The entire string "admin' OR '1'='1' --" is treated as the username value.
No SQL injection possible because it's not parsed as SQL code!

OTHER SQL INJECTION EXAMPLES PREVENTED:

1. Data Extraction:
   Input: admin'; SELECT * FROM credit_cards; --
   Without PreparedStatement: Dumps credit card table
   With PreparedStatement: Searches for username literally

2. Data Deletion:
   Input: admin'; DROP TABLE users; --
   Without PreparedStatement: Deletes entire users table!
   With PreparedStatement: Searches for that literal string

3. Privilege Escalation:
   Input: admin'; UPDATE users SET role='admin' WHERE username='attacker'; --
   Without PreparedStatement: Grants admin privileges
   With PreparedStatement: Harmless string search

ADDITIONAL SECURITY BEST PRACTICES:

1. Password Hashing:
   ✓ Never store passwords in plain text
   ✓ Use salted hashes
   ✓ In production: use bcrypt, scrypt, or Argon2
   ✓ SHA-256 is shown for simplicity but not recommended for passwords

2. Generic Error Messages:
   ✓ Don't say "username not found" or "wrong password"
   ✓ Always say "invalid username or password"
   ✓ Prevents username enumeration attacks

3. Additional Protections:
   - Rate limiting (prevent brute force)
   - Account lockout after failed attempts
   - Use Console.readPassword() to hide password input
   - HTTPS for web applications
   - Session management
   - CSRF protection

SETUP AND USAGE:

1. Add SQLite JDBC driver to classpath:
   - Download: https://github.com/xerial/sqlite-jdbc
   - Or Maven: org.xerial:sqlite-jdbc:3.43.0.0

2. Compile:
   javac SecureLogin.java

3. Run:
   java -cp .:sqlite-jdbc.jar SecureLogin

4. First time: Select option 1 to setup
5. Then: Select option 2 to test login

TEST SCENARIOS:

Valid login:
Username: admin
Password: admin123
Result: ✓ LOGIN SUCCESSFUL

Invalid password:
Username: admin
Password: wrongpass
Result: ✗ LOGIN FAILED (generic message)

SQL injection attempt:
Username: admin' OR '1'='1' --
Password: anything
Result: ✗ LOGIN FAILED (injection prevented!)

The key takeaway: Always use PreparedStatement with parameterized
queries for any database operation involving user input!
*/