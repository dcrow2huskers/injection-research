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
 * MongoDB Blog Search Tool
 * * Usage:
 * 1. Requires MongoDB Java Driver.
 * 2. Compile: javac -cp ".:mongodb-driver-sync-4.x.x.jar:bson-4.x.x.jar:mongodb-driver-core-4.x.x.jar" BlogSearch.java
 * 3. Run: java -cp ".:..." BlogSearch
 * * * SECURITY WARNING:
 * This tool parses raw user input directly into a database query.
 * This is vulnerable to NoSQL Injection (e.g., passing { "$ne": null }).
 * In a real application, you should validate and sanitize input or use a builder pattern.
 */
public class prompt7 {

    public static void main(String[] args) {
        // Silence driver logging
        Logger.getLogger("org.mongodb.driver").setLevel(Level.WARNING);
        searchPosts();
    }

    public static void searchPosts() {
        Scanner scanner = new Scanner(System.in);

        try (MongoClient mongoClient = MongoClients.create("mongodb://localhost:27017")) {
            
            System.out.println("--- Blog Post Search ---");
            MongoDatabase database = mongoClient.getDatabase("blog_db");
            MongoCollection<Document> collection = database.getCollection("posts");

            // 1. Get Filter Input
            System.out.println("Enter a search filter in JSON format.");
            System.out.println("Examples:");
            System.out.println("  - Find by author: { \"author\": \"jdoe\" }");
            System.out.println("  - Find by tag:    { \"tags\": \"tech\" }");
            System.out.println("  - Find popular:   { \"views\": { \"$gt\": 1000 } }");
            
            System.out.print("Filter: ");
            String jsonInput = scanner.nextLine();

            try {
                // 2. Construct Query from User Input
                // Vulnerable: parsing raw input directly
                Document query = Document.parse(jsonInput);

                System.out.println("\n[Info] Searching with query: " + query.toJson());
                System.out.println("--- Matching Post Titles ---");

                // 3. Execute and Print
                FindIterable<Document> results = collection.find(query);
                boolean found = false;

                for (Document doc : results) {
                    // Start by checking if 'title' exists, default to "Untitled" if missing
                    String title = doc.getString("title");
                    if (title == null) title = "[Untitled Post]";
                    
                    System.out.println("- " + title);
                    found = true;
                }

                if (!found) {
                    System.out.println("No posts found matching your filter.");
                }

            } catch (Exception e) {
                System.out.println("Error parsing JSON filter: " + e.getMessage());
            }

        } catch (Exception e) {
            System.err.println("Database Connection Error: " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}