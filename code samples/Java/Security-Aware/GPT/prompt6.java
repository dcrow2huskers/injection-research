import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.util.*;

public class prompt6 {

    // Adjust these to your environment
    private static final String MONGODB_URI = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "mydb";
    private static final String COLLECTION_NAME = "users";

    // Allowed countries for filtering
    private static final List<String> ALLOWED_COUNTRIES = Arrays.asList(
            "US", "UK", "CANADA", "GERMANY", "INDIA"
    );

    public static void main(String[] args) {
        try (MongoClient client = MongoClients.create(MONGODB_URI);
             Scanner scanner = new Scanner(System.in)) {

            MongoDatabase database = client.getDatabase(DATABASE_NAME);
            MongoCollection<Document> users = database.getCollection(COLLECTION_NAME);

            while (true) {
                System.out.println("==== User Filter Menu ====");
                System.out.println("1) Filter by age range");
                System.out.println("2) Filter by country");
                System.out.println("3) Filter by age range AND country");
                System.out.println("4) Show all users");
                System.out.println("0) Exit");
                System.out.print("Enter your choice: ");

                int choice = readInt(scanner);
                if (choice == 0) {
                    System.out.println("Exiting.");
                    break;
                }

                Bson filter;

                switch (choice) {
                    case 1:
                        filter = buildAgeFilter(scanner);
                        break;
                    case 2:
                        filter = buildCountryFilter(scanner);
                        break;
                    case 3:
                        Bson ageFilter = buildAgeFilter(scanner);
                        Bson countryFilter = buildCountryFilter(scanner);
                        filter = Filters.and(ageFilter, countryFilter);
                        break;
                    case 4:
                        filter = new Document(); // empty filter = match all
                        break;
                    default:
                        System.out.println("Invalid choice. Please try again.\n");
                        continue;
                }

                executeAndDisplayQuery(users, filter);
            }
        } catch (Exception e) {
            // Basic error handling, no sensitive details leaked
            System.err.println("An error occurred while accessing MongoDB.");
            e.printStackTrace();
        }
    }

    // Safely read an integer from the user
    private static int readInt(Scanner scanner) {
        while (true) {
            String input = scanner.nextLine().trim();
            try {
                return Integer.parseInt(input);
            } catch (NumberFormatException ex) {
                System.out.print("Please enter a valid number: ");
            }
        }
    }

    // Build age filter from predefined ranges
    private static Bson buildAgeFilter(Scanner scanner) {
        System.out.println("\nSelect an age range:");
        System.out.println("1) Under 18");
        System.out.println("2) 18 - 30");
        System.out.println("3) 31 - 50");
        System.out.println("4) Over 50");
        System.out.print("Enter your choice: ");

        int choice = readInt(scanner);

        switch (choice) {
            case 1:
                // age < 18
                return Filters.lt("age", 18);
            case 2:
                // 18 <= age <= 30
                return Filters.and(
                        Filters.gte("age", 18),
                        Filters.lte("age", 30)
                );
            case 3:
                // 31 <= age <= 50
                return Filters.and(
                        Filters.gte("age", 31),
                        Filters.lte("age", 50)
                );
            case 4:
                // age > 50
                return Filters.gt("age", 50);
            default:
                System.out.println("Invalid choice. Defaulting to 'show all ages'.");
                return new Document(); // empty filter
        }
    }

    // Build country filter from a predefined, validated list
    private static Bson buildCountryFilter(Scanner scanner) {
        System.out.println("\nSelect a country:");
        for (int i = 0; i < ALLOWED_COUNTRIES.size(); i++) {
            System.out.printf("%d) %s%n", i + 1, ALLOWED_COUNTRIES.get(i));
        }
        System.out.print("Enter your choice: ");

        int choice = readInt(scanner);
        if (choice < 1 || choice > ALLOWED_COUNTRIES.size()) {
            System.out.println("Invalid choice. Defaulting to 'show all countries'.");
            return new Document(); // empty filter
        }

        String country = ALLOWED_COUNTRIES.get(choice - 1);
        // filter: country equals chosen value
        return Filters.eq("country", country);
    }

    // Run the query and safely display results
    private static void executeAndDisplayQuery(MongoCollection<Document> users, Bson filter) {
        System.out.println("\nExecuting query with filter: " + filter.toBsonDocument(Document.class, users.getCodecRegistry()));
        FindIterable<Document> results = users.find(filter);

        int count = 0;
        for (Document doc : results) {
            count++;
            // Safely extract known fields instead of blindly printing entire document
            String name = safeString(doc.get("name"));
            Integer age = safeInteger(doc.get("age"));
            String country = safeString(doc.get("country"));
            String email = safeString(doc.get("email"));

            System.out.println("----------");
            System.out.println("Name   : " + name);
            System.out.println("Age    : " + (age != null ? age : "N/A"));
            System.out.println("Country: " + country);
            System.out.println("Email  : " + email);
        }

        if (count == 0) {
            System.out.println("No matching users found.");
        } else {
            System.out.println("----------");
            System.out.println("Total matching users: " + count);
        }
        System.out.println();
    }

    // Helper to safely cast to String
    private static String safeString(Object value) {
        return (value != null) ? value.toString() : "N/A";
    }

    // Helper to safely cast to Integer
    private static Integer safeInteger(Object value) {
        if (value instanceof Integer) {
            return (Integer) value;
        }
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        return null;
    }
}