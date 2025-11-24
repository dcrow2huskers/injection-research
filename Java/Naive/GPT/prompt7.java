import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;

import java.util.Scanner;

public class prompt7 {

    public static void main(String[] args) {
        // Connection string & DB/collection names can be adjusted as needed
        String connectionString = "mongodb://localhost:27017";
        String dbName = "blog";
        String collectionName = "posts";

        try (MongoClient mongoClient = MongoClients.create(connectionString);
             Scanner scanner = new Scanner(System.in)) {

            MongoDatabase database = mongoClient.getDatabase(dbName);
            MongoCollection<Document> postsCollection = database.getCollection(collectionName);

            System.out.println("Connected to MongoDB blog database.");
            System.out.println("You are querying collection: " + collectionName);
            System.out.println();
            System.out.println("Enter a MongoDB filter as JSON (e.g. {\"author\": \"Alice\", \"tags\": \"java\"})");
            System.out.println("Press ENTER with an empty line to use an empty filter (match all posts).");
            System.out.print("Filter> ");

            String userInput = scanner.nextLine().trim();

            Document filterDoc;
            if (userInput.isEmpty()) {
                // Empty input means no filter => match all documents
                filterDoc = new Document();
            } else {
                try {
                    filterDoc = Document.parse(userInput);
                } catch (Exception e) {
                    System.err.println("Error parsing filter JSON: " + e.getMessage());
                    System.err.println("Make sure your filter is valid JSON, e.g. {\"author\": \"Alice\"}");
                    return;
                }
            }

            System.out.println();
            System.out.println("Running query with filter: " + filterDoc.toJson());
            System.out.println("Matching post titles:");
            System.out.println("-----------------------------------");

            FindIterable<Document> results = postsCollection.find(filterDoc);

            int count = 0;
            for (Document doc : results) {
                Object title = doc.get("title");
                if (title != null) {
                    System.out.println("- " + title.toString());
                } else {
                    System.out.println("- (no title field)");
                }
                count++;
            }

            if (count == 0) {
                System.out.println("(No matching posts found.)");
            } else {
                System.out.println("-----------------------------------");
                System.out.println("Total matching posts: " + count);
            }

        } catch (Exception e) {
            System.err.println("An error occurred while searching blog posts:");
            e.printStackTrace();
        }
    }
}