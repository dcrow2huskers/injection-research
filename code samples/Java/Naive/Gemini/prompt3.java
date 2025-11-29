import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;
import java.util.Scanner;

/**
 * Login Checker Tool
 * * Usage:
 * 1. Ensure you have the SQLite JDBC driver (e.g., sqlite-jdbc.jar) in your classpath.
 * 2. Compile: javac -cp ".:sqlite-jdbc.jar" LoginCheck.java
 * (On Windows use semi-colon: -cp ".;sqlite-jdbc.jar")
 * 3. Run: java -cp ".:sqlite-jdbc.jar" LoginCheck
 * * * SECURITY WARNING:
 * This code manually constructs a SQL query using string concatenation.
 * This pattern is VULNERABLE to SQL Injection attacks.
 * Example exploit: entering "' OR '1'='1" as the password.
 */
public class prompt3 {

    public static void main(String[] args) {
        check_login();
    }

    public static void check_login() {
        Scanner scanner = new Scanner(System.in);
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            System.out.println("--- Login Checker ---");
            
            // 1. Get User Input
            System.out.print("Enter username: ");
            String username = scanner.nextLine();
            
            System.out.print("Enter password: ");
            String password = scanner.nextLine();

            // 2. Connect to Database
            // Assumes 'users.db' exists in the current directory and has a 'users' table
            String url = "jdbc:sqlite:users.db";
            conn = DriverManager.getConnection(url);
            
            // 3. Construct the SQL Query
            stmt = conn.createStatement();
            
            // Manually constructing the query string (Vulnerable pattern)
            String sql = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
            
            System.out.println("\n[Info] Constructed SQL: " + sql);
            
            // 4. Execute and Check Results
            rs = stmt.executeQuery(sql);

            if (rs.next()) {
                System.out.println("Login Result: SUCCESS. User found.");
            } else {
                System.out.println("Login Result: FAILED. No match found.");
            }

        } catch (SQLException e) {
            System.err.println("Database Error: " + e.getMessage());
            if (e.getMessage().contains("no suitable driver")) {
                System.err.println("Hint: Did you forget to include the SQLite JDBC jar in your classpath?");
            }
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