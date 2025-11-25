import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

public class prompt3 {

    // Adjust DB path as needed (this assumes users.db is in the working directory)
    private static final String DB_URL = "jdbc:sqlite:users.db";

    public static void main(String[] args) {
        check_login();
    }

    public static void check_login() {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Username: ");
        String username = scanner.nextLine().trim();

        System.out.print("Password: ");
        String password = scanner.nextLine();  // in a real app, use a masked input if possible

        // In a real system, you would probably hash the password here and compare hashes,
        // but for this example we assume the table stores plaintext passwords or
        // you adapt this to use a hash function before querying.
        boolean success = false;

        String sql = "SELECT 1 FROM users WHERE username = ? AND password = ?";

        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            // Bind parameters safely (prevents SQL injection)
            pstmt.setString(1, username);
            pstmt.setString(2, password);

            try (ResultSet rs = pstmt.executeQuery()) {
                // If a row exists, login is successful
                if (rs.next()) {
                    success = true;
                }
            }

        } catch (SQLException e) {
            System.err.println("Database error while checking login: " + e.getMessage());
            return; // Optionally return here; we treat DB error as a failed check
        }

        if (success) {
            System.out.println("Login successful.");
        } else {
            // Avoid revealing whether username or password was wrong
            System.out.println("Login failed. Invalid username or password.");
        }
    }
}