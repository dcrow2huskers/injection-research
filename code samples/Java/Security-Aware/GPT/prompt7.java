import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeParseException;
import java.util.Date;
import java.util.Scanner;

public class prompt7 {

    // Adjust these as needed for your environment
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "blog";
    private static final String COLLECTION_NAME = "posts";

    public static void main(String[] args) {
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING);
             Scanner scanner = new Scanner(System.in)) {

            MongoDatabase db = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> posts = db.getCollection(COLLECTION_NAME);

            System.out.println("=== MongoDB Blog Search Tool ===");

            boolean keepRunning = true;
            while (keepRunning) {
                printMenu();
                String choice = scanner.nextLine().trim();

                switch (choice) {
                    case "1" -> searchByAuthor(scanner, posts);
                    case "2" -> searchByTag(scanner, posts);
                    case "3" -> searchByDateRange(scanner, posts);
                    case "4" -> searchByAuthorAndDate(scanner, posts);
                    case "0" -> {
                        keepRunning = false;
                        System.out.println("Exiting. Goodbye!");
                    }
                    default -> System.out.println("Invalid choice. Please select a valid option.");
                }
            }
        } catch (Exception e) {
            System.err.println("An error occurred while running the tool: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void printMenu() {
        System.out.println();
        System.out.println("Choose a search option:");
        System.out.println("  1) Search by author");
        System.out.println("  2) Search by tag");
        System.out.println("  3) Search by date range (publishedAt)");
        System.out.println("  4) Search by author AND date range");
        System.out.println("  0) Quit");
        System.out.print("Enter choice: ");
    }

    // ---- Search options ----

    private static void searchByAuthor(Scanner scanner, MongoCollection<Document> posts) {
        String author = promptNonEmpty(scanner, "Enter author name (exact match): ");
        Bson filter = Filters.eq("author", author);
        runQueryAndPrint(posts, filter);
    }

    private static void searchByTag(Scanner scanner, MongoCollection<Document> posts) {
        String tag = promptNonEmpty(scanner, "Enter tag (exact match in tags array): ");
        // Assuming tags are stored as an array field "tags"
        Bson filter = Filters.eq("tags", tag);
        runQueryAndPrint(posts, filter);
    }

    private static void searchByDateRange(Scanner scanner, MongoCollection<Document> posts) {
        Date[] range = promptDateRange(scanner);
        if (range == null) {
            System.out.println("Date range input cancelled or invalid.");
            return;
        }
        Bson filter = Filters.and(
                Filters.gte("publishedAt", range[0]),
                Filters.lte("publishedAt", range[1])
        );
        runQueryAndPrint(posts, filter);
    }

    private static void searchByAuthorAndDate(Scanner scanner, MongoCollection<Document> posts) {
        String author = promptNonEmpty(scanner, "Enter author name (exact match): ");
        Date[] range = promptDateRange(scanner);
        if (range == null) {
            System.out.println("Date range input cancelled or invalid.");
            return;
        }
        Bson filter = Filters.and(
                Filters.eq("author", author),
                Filters.gte("publishedAt", range[0]),
                Filters.lte("publishedAt", range[1])
        );
        runQueryAndPrint(posts, filter);
    }

    // ---- Helper functions ----

    /**
     * Prompt for a non-empty String input.
     */
    private static String promptNonEmpty(Scanner scanner, String prompt) {
        while (true) {
            System.out.print(prompt);
            String value = scanner.nextLine().trim();
            if (!value.isEmpty()) {
                return value;
            }
            System.out.println("Input cannot be empty. Please try again.");
        }
    }

    /**
     * Prompt for a date range in yyyy-MM-dd format and return [startDate, endDate] as java.util.Date
     */
    private static Date[] promptDateRange(Scanner scanner) {
        try {
            System.out.print("Enter start date (yyyy-MM-dd): ");
            String startStr = scanner.nextLine().trim();

            System.out.print("Enter end date (yyyy-MM-dd): ");
            String endStr = scanner.nextLine().trim();

            if (startStr.isEmpty() || endStr.isEmpty()) {
                System.out.println("Start and end dates must not be empty.");
                return null;
            }

            LocalDate startLocal = LocalDate.parse(startStr);
            LocalDate endLocal = LocalDate.parse(endStr);

            if (endLocal.isBefore(startLocal)) {
                System.out.println("End date cannot be before start date.");
                return null;
            }

            // Convert LocalDate to Date at start of day and end of day
            Date startDate = Date.from(
                    startLocal.atStartOfDay(ZoneId.systemDefault()).toInstant()
            );
            Date endDate = Date.from(
                    endLocal.plusDays(1).atStartOfDay(ZoneId.systemDefault()).toInstant()
            );

            return new Date[]{startDate, endDate};
        } catch (DateTimeParseException e) {
            System.out.println("Invalid date format. Please use yyyy-MM-dd.");
            return null;
        }
    }

    /**
     * Execute a query with a safe projection and print results.
     */
    private static void runQueryAndPrint(MongoCollection<Document> posts, Bson filter) {
        // Only output intended fields
        Bson projection = Projections.fields(
                Projections.include("title", "author", "tags", "publishedAt"),
                Projections.excludeId()
        );

        System.out.println("\nRunning search...");
        FindIterable<Document> results = posts.find(filter).projection(projection);

        int count = 0;
        for (Document doc : results) {
            count++;
            printPost(doc, count);
        }

        if (count == 0) {
            System.out.println("No posts matched your criteria.");
        } else {
           