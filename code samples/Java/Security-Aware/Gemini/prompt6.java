import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.FindIterable;
import com.mongodb.client.model.Filters;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * MongoUserFilter
 * A secure command-line tool to query a MongoDB database.
 * * * Security Features:
 * 1. NoSQL Injection Prevention: Uses the 'Filters' builder API instead of string concatenation.
 * 2. Strict Input Validation: Ensures age inputs are integers and criteria are safe.
 * 3. Least Privilege Display: Only prints specific, non-sensitive fields.
 */
public class prompt6 {

    // Connection String (Update with your actual MongoDB URI)
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DB_NAME = "user_directory";
    private static final String COLLECTION_NAME = "users";

    public static void main(String[] args) {
        // Disable noisy MongoDB logging for cleaner console output
        Logger.getLogger("org.mongodb.driver").setLevel(Level.WARNING);

        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DB_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);

            Scanner scanner = new Scanner(System.in);
            boolean running = true;

            System.out.println("--- Mongo User Filter Tool ---");

            while (running) {
                System.out.println("\nSelect Filter Mode:");
                System.out.println("1. Filter by Age Range");
                System.out.println("2. Filter by Country");
                System.out.println("3. Exit");
                System.out.print("> ");

                String choice = scanner.nextLine().trim();

                switch (choice) {
                    case "1":
                        filterByAge(collection, scanner);
                        break;
                    case "2":
                        filterByCountry(collection, scanner);
                        break;
                    case "3":
                        running = false;
                        break;
                    default:
                        System.out.println("Invalid option.");
                }
            }
            scanner.close();
            System.out.println("Exiting...");

        } catch (Exception e) {
            System.err.println("Connection Error: " + e.getMessage());
            System.err.println("Ensure MongoDB is running and the Java Driver is in your classpath.");
        }
    }

    /**
     * securely builds a range query for age.
     */
    private static void filterByAge(MongoCollection<Document> collection, Scanner scanner) {
        try {
            System.out.print("Enter minimum age: ");
            int minAge = Integer.parseInt(scanner.nextLine().trim());

            System.out.print("Enter maximum age: ");
            int maxAge = Integer.parseInt(scanner.nextLine().trim());

            if (minAge < 0 || maxAge < 0 || minAge > maxAge) {
                System.out.println("Error: Invalid age range.");
                return;
            }

            // CONSTRUCTION: Using Filters.and, Filters.gte, Filters.lte
            // This builds the BSON object { "age": { "$gte": min, "$lte": max } } securely.
            Bson query = Filters.and(
                    Filters.gte("age", minAge),
                    Filters.lte("age", maxAge)
            );

            System.out.println("Executing query for ages " + minAge + " to " + maxAge + "...");
            executeAndDisplay(collection, query);

        } catch (NumberFormatException e) {
            System.out.println("Error: Age must be a valid integer.");
        }
    }

    /**
     * Securely builds an equality query for country.
     */
    private static void filterByCountry(MongoCollection<Document> collection, Scanner scanner) {
        System.out.print("Enter Country Name: ");
        String country = scanner.nextLine().trim();

        if (country.isEmpty()) {
            System.out.println("Error: Country cannot be empty.");
            return;
        }

        // CONSTRUCTION: Using Filters.eq
        // This handles special characters in 'country' automatically, preventing injection.
        // E.g. inputting "{ $ne: null }" treats it as the literal string "{ $ne: null }".
        Bson query = Filters.eq("country", country);

        System.out.println("Executing query for country: " + country + "...");
        executeAndDisplay(collection, query);
    }

    /**
     * Runs the query and safely displays specific fields.
     */
    private static void executeAndDisplay(MongoCollection<Document> collection, Bson query) {
        FindIterable<Document> results = collection.find(query);
        boolean found = false;

        System.out.println("\n--- Results ---");
        System.out.printf("%-20s | %-5s | %-15s%n", "Name", "Age", "Country");
        System.out.println("------------------------------------------------");

        for (Document doc : results) {
            found = true;
            // SAFE EXTRACTION: Explicitly getting expected types prevents
            // displaying unexpected objects or massive binary data.
            String name = doc.getString("name");
            Integer age = doc.getInteger("age");
            String country = doc.getString("country");

            // Handle potential nulls in data
            name = (name != null) ? name : "Unknown";
            String ageStr = (age != null) ? age.toString() : "N/A";
            country = (country != null) ? country : "Unknown";

            System.out.printf("%-20s | %-5s | %-15s%n", name, ageStr, country);
        }

        if (!found) {
            System.out.println("(No matches found)");
        }
    }
}