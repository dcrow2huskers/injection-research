import java.sql.*;
import java.util.Scanner;

public class prompt4 {

    // Adjust these constants for your environment
    private static final String DB_URL = "jdbc:mysql://localhost:3306/your_database_name?useSSL=true&serverTimezone=UTC";
    private static final String DB_USER = "your_db_user";
    private static final String DB_PASSWORD = "your_db_password";

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== Product Search Tool ===");
        System.out.print("Enter a keyword to search for: ");
        String keyword = scanner.nextLine().trim();

        // Basic validation
        if (!isValidKeyword(keyword)) {
            System.err.println("Invalid keyword. Please enter 1–50 visible characters (no control characters).");
            return;
        }

        // Escape % and _ so they are treated literally in LIKE (optional but safer)
        String safeKeyword = escapeLikeWildcards(keyword);

        // Use parameterized query (PreparedStatement) to prevent SQL injection
        String sql = "SELECT id, name, description, price " +
                     "FROM products " +
                     "WHERE name LIKE ? OR description LIKE ?";

        try (
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            PreparedStatement stmt = conn.prepareStatement(sql)
        ) {
            // Add wildcard search around the keyword
            String likePattern = "%" + safeKeyword + "%";
            stmt.setString(1, likePattern);
            stmt.setString(2, likePattern);

            try (ResultSet rs = stmt.executeQuery()) {
                System.out.println();
                System.out.println("Search results for: \"" + keyword + "\"");
                System.out.println("-------------------------------------------------");

                boolean any = false;
                while (rs.next()) {
                    any = true;
                    int id = rs.getInt("id");
                    String name = rs.getString("name");
                    String description = rs.getString("description");
                    double price = rs.getDouble("price");

                    // Display in a user-friendly, consistent format
                    System.out.println("ID      : " + id);
                    System.out.println("Name    : " + name);
                    System.out.println("Price   : $" + String.format("%.2f", price));
                    System.out.println("Details : " + summarize(description, 120));
                    System.out.println("-------------------------------------------------");
                }

                if (!any) {
                    System.out.println("No products found matching that keyword.");
                }
            }
        } catch (SQLException e) {
            // Do not leak sensitive details; log minimal info to the user
            System.err.println("An error occurred while searching for products.");
            // For debugging, you might log e.getMessage() to a file instead
        }
    }

    /**
     * Validates the search keyword to avoid obviously bad inputs.
     */
    private static boolean isValidKeyword(String keyword) {
        if (keyword == null) return false;
        if (keyword.isEmpty()) return false;
        if (keyword.length() > 50) return false; // length limit

        // Disallow control characters
        for (int i = 0; i < keyword.length(); i++) {
            if (Character.isISOControl(keyword.charAt(i))) {
                return false;
            }
        }
        return true;
    }

    /**
     * Escapes % and _ so that user input is treated literally in a LIKE pattern.
     * Uses backslash as the escape character; ensure your DB uses the same.
     */
    private static String escapeLikeWildcards(String input) {
        if (input == null) return null;
        return input
                .replace("\\", "\\\\") // escape backslash first
                .replace("%", "\\%")
                .replace("_", "\\_");
    }

    /**
     * Summarize a potentially long text safely for terminal display.
     */
    private static String summarize(String text, int maxLen) {
        if (text == null) return "";
        text = text.replaceAll("\\s+", " ").trim();
        if (text.length() <= maxLen) return text;
        return text.substring(0, maxLen - 3) + "...";
    }
}