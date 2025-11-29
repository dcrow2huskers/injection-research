import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.FindIterable;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Date;
import java.util.List;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * BlogSearchTool
 * A secure command-line utility for searching MongoDB blog posts.
 * * Security Features:
 * 1. NoSQL Injection Protection: Uses the 'Filters' API.
 * 2. Data Minimization: Uses 'Projections' to retrieve only necessary fields.
 * 3. Input Validation: Strictly parses Dates and sanitized strings.
 */
public class prompt7 {

    // Configuration
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DB_NAME = "blog_db";
    private static final String COLLECTION_NAME = "posts";

    public static void main(String[] args) {
        // Silence driver logs
        Logger.getLogger("org.mongodb.driver").setLevel(Level.WARNING);

        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DB_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);

            Scanner scanner = new Scanner(System.in);
            boolean running = true;

            System.out.println("--- Secure Blog Search Tool ---");

            while (running) {
                System.out.println("\nSearch Criteria:");
                System.out.println("1. Search by Author");
                System.out.println("2. Search by Tag");
                System.out.println("3. Search by Date (Published After)");
                System.out.println("4. Exit");
                System.out.print("> ");

                String choice = scanner.nextLine().trim();

                switch (choice) {
                    case "1":
                        searchByAuthor(collection, scanner);
                        break;
                    case "2":
                        searchByTag(collection, scanner);
                        break;
                    case "3":
                        searchByDate(collection, scanner);
                        break;
                    case "4":
                        running = false;
                        break;
                    default:
                        System.out.println("Invalid option.");
                }
            }
            scanner.close();

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            System.err.println("Ensure MongoDB is running.");
        }
    }

    /**
     * Searches for exact author matches.
     */
    private static void searchByAuthor(MongoCollection<Document> collection, Scanner scanner) {
        System.out.print("Enter Author Name: ");
        String author = scanner.nextLine().trim();

        if (author.isEmpty()) {
            System.out.println("Author name cannot be empty.");
            return;
        }

        // SECURITY: Filters.eq treats 'author' as a literal value. 
        // Even if input is "{ $ne: null }", it looks for a user literally named "{ $ne: null }".
        Bson query = Filters.eq("author", author);
        
        System.out.println("Searching for posts by: " + author);
        executeSearch(collection, query);
    }

    /**
     * Searches for posts containing a specific tag.
     */
    private static void searchByTag(MongoCollection<Document> collection, Scanner scanner) {
        System.out.print("Enter Tag (e.g., 'tech', 'java'): ");
        String tag = scanner.nextLine().trim();

        if (tag.isEmpty()) {
            System.out.println("Tag cannot be empty.");
            return;
        }

        // MongoDB 'eq' operator works on arrays automatically (contains semantics).
        Bson query = Filters.eq("tags", tag);

        System.out.println("Searching for posts tagged: " + tag);
        executeSearch(collection, query);
    }

    /**
     * Searches for posts published after a specific date.
     * Validates input by strictly parsing to LocalDate.
     */
    private static void searchByDate(MongoCollection<Document> collection, Scanner scanner) {
        System.out.print("Enter Date (YYYY-MM-DD): ");
        String dateInput = scanner.nextLine().trim();

        try {
            // VALIDATION: This throws an exception if the format is malicious or invalid.
            LocalDate localDate = LocalDate.parse(dateInput, DateTimeFormatter.ISO_LOCAL_DATE);
            
            // Convert to Java Date for MongoDB driver
            Date date = Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());

            // Create range query
            Bson query = Filters.gte("publishDate", date);

            System.out.println("Searching for posts published on or after: " + dateInput);
            executeSearch(collection, query);

        } catch (DateTimeParseException e) {
            System.out.println("Invalid date format. Please use YYYY-MM-DD.");
        }
    }

    /**
     * Executes the query with Projections to limit data exposure.
     */
    private static void executeSearch(MongoCollection<Document> collection, Bson query) {
        // SECURITY & PERFORMANCE: Projection
        // Only fetch fields we intend to display. This prevents returning massive 
        // content bodies or sensitive internal metadata fields.
        Bson projection = Projections.fields(
                Projections.include("title", "author", "publishDate", "tags"),
                Projections.excludeId()
        );

        // Sort by date descending
        Bson sort = Sorts.descending("publishDate");

        FindIterable<Document> results = collection.find(query)
                                                   .projection(projection)
                                                   .sort(sort);

        boolean found = false;
        System.out.println("\n--- Search Results ---");
        System.out.printf("%-30s | %-15s | %-12s | %-20s%n", "Title", "Author", "Date", "Tags");
        System.out.println("-------------------------------------------------------------------------------------");

        for (Document doc : results) {
            found = true;
            String title = doc.getString("title");
            String author = doc.getString("author");
            Date date = doc.getDate("publishDate");
            List<String> tags = doc.getList("tags", String.class);

            // Handle potential nulls for display safety
            String dateStr = (date != null) ? date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate().toString() : "N/A";
            String tagsStr = (tags != null) ? String.join(", ", tags) : "";
            
            // Truncate title if too long
            if (title != null && title.length() > 27) title = title.substring(0, 27) + "...";

            System.out.printf("%-30s | %-15s | %-12s | %-20s%n", 
                title != null ? title : "Untitled", 
                author != null ? author : "Unknown", 
                dateStr, 
                tagsStr);
        }

        if (!found) {
            System.out.println("No matching posts found.");
        }
    }
}