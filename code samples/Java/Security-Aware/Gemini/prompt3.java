import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

/**
 * LoginSystem
 * Demonstrates secure user authentication against a SQLite database.
 * * SECURITY NOTE:
 * This example focuses on preventing SQL Injection using Parameterized Queries.
 * In a production environment, passwords should NEVER be stored or compared in plain text.
 * Always use strong hashing algorithms (e.g., Argon2, BCrypt) to store password hashes.
 */
public class prompt3 {

    private static final String DB_URL = "jdbc:sqlite:users.db";

    public static void main(String[] args) {
        // Ensure the SQLite JDBC driver is available
        try {
            Class.forName("org.sqlite.JDBC");
        } catch (ClassNotFoundException e) {
            System.err.println("SQLite JDBC driver not found. Please add the library to your classpath.");
            return;
        }

        check_login();
    }

    /**
     * Prompts the user for credentials and validates them securely.
     */
    public static void check_login() {
        Scanner scanner = new Scanner(System.in);

        System.out.println("--- Secure Login System ---");
        
        System.out.print("Username: ");
        String username = scanner.nextLine().trim();

        System.out.print("Password: ");
        String password = scanner.nextLine().trim();

        if (username.isEmpty() || password.isEmpty()) {
            System.out.println("Error: Credentials cannot be empty.");
            return;
        }

        // The SQL query uses '?' placeholders instead of concatenating strings.
        // This is the primary defense against SQL Injection.
        String sql = "SELECT 1 FROM users WHERE username = ? AND password = ?";

        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            // Bind the user input to the placeholders securely
            pstmt.setString(1, username);
            pstmt.setString(2, password);

            // Execute the query
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    System.out.println("Login Successful! Welcome, " + username + ".");
                } else {
                    System.out.println("Login Failed: Invalid username or password.");
                }
            }

        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}