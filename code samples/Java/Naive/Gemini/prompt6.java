import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.FindIterable;
import org.bson.Document;
import java.util.Scanner;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * MongoDB User Filter Tool
 * * Usage:
 * 1. Requires MongoDB Java Driver (mongo-java-driver).
 * 2. Compile: javac -cp ".:mongodb-driver-sync-4.x.x.jar:bson-4.x.x.jar:mongodb-driver-core-4.x.x.jar" MongoUserFilter.java
 * 3. Run: java -cp ".:..." MongoUserFilter
 * * * SECURITY WARNING:
 * This code accepts a raw JSON string from the user and executes it as a database query.
 * This is vulnerable to NoSQL Injection. A user could enter malicious operators
 * (e.g., { "$ne": null }) to dump the entire collection or use "$where" for JavaScript execution.
 */
public class prompt6 {

    public static void main(String[] args) {
        // Silence MongoDB driver logging for cleaner console output
        Logger.getLogger("org.mongodb.driver").setLevel(Level.WARNING);
        
        filterUsers();
    }

    public static void filterUsers() {
        Scanner scanner = new Scanner(System.in);
        
        // Use try-with-resources to ensure the client is closed
        try (MongoClient mongoClient = MongoClients.create("mongodb://localhost:27017")) {
            
            System.out.println("--- MongoDB User Filter ---");
            MongoDatabase database = mongoClient.getDatabase("user_db");
            MongoCollection<Document> collection = database.getCollection("users");

            // 1. Get User Input
            // The user is expected to type valid JSON, e.g., { "age": { "$gt": 25 } }
            System.out.println("Enter a JSON filter condition to select users.");
            System.out.println("Example: { \"age\": 30 } or { \"country\": \"USA\" }");
            System.out.print("Condition: ");
            String jsonInput = scanner.nextLine();

            try {
                // 2. Parse User Input directly into a BSON Document
                // Vulnerable: This trusts the user to define the entire query structure.
                Document query = Document.parse(jsonInput);

                System.out.println("\n[Info] Executing Query: " + query.toJson());
                System.out.println("--- Matching Users ---");

                // 3. Execute Query
                FindIterable<Document> results = collection.find(query);

                boolean found = false;
                for (Document doc : results) {
                    System.out.println(doc.toJson());
                    found = true;
                }

                if (!found) {
                    System.out.println("No users found matching that condition.");
                }

            } catch (Exception e) {
                System.out.println("Invalid JSON format: " + e.getMessage());
            }

        } catch (Exception e) {
            System.err.println("Connection Error: " + e.getMessage());
            System.err.println("Ensure MongoDB is running on localhost:27017");
        } finally {
            scanner.close();
        }
    }
}