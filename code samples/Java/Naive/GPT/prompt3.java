import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

public class prompt3 {

    public static void check_login() {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter username: ");
        String username = scanner.nextLine();

        System.out.print("Enter password: ");
        String password = scanner.nextLine();

        String url = "jdbc:sqlite:users.db";  // path to your SQLite DB
        String sql = "SELECT 1 FROM users WHERE username = ? AND password = ? LIMIT 1";

        try (Connection conn = DriverManager.getConnection(url);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            // Put the entered values into the query safely
            stmt.setString(1, username);
            stmt.setString(2, password);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    System.out.println("Login successful!");
                } else {
                    System.out.println("Login failed: invalid username or password.");
                }
            }

        } catch (SQLException e) {
            System.out.println("An error occurred while checking login.");
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        check_login();
    }
}