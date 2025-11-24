import java.sql.*;
import java.util.Scanner;

public class prompt4 {

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/your_database";
        String user = "your_username";
        String password = "your_password";

        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter search keyword: ");
        String keyword = scanner.nextLine();

        // SQL using placeholders (safe)
        String sql = "SELECT name, price FROM products " +
                     "WHERE name LIKE ? OR description LIKE ?";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            String pattern = "%" + keyword + "%";
            stmt.setString(1, pattern);
            stmt.setString(2, pattern);

            ResultSet rs = stmt.executeQuery();

            System.out.println("\nMatching products:\n");

            boolean foundAny = false;
            while (rs.next()) {
                foundAny = true;
                String name = rs.getString("name");
                double price = rs.getDouble("price");
                System.out.println(name + " - $" + price);
            }

            if (!foundAny) {
                System.out.println("No products found.");
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}