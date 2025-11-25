public import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;

import java.util.Scanner;

public class prompt6 {

    public static void main(String[] args) {
        // Adjust this connection string to your environment (auth, host, port, etc.)
        String connectionString = "mongodb://localhost:27017";

        // Database and collection names
        String dbName = "mydb";
        String collectionName = "users";

        Scanner scanner = new Scanner(System.in);

        System.out.println("Connecting to MongoDB at: " + connectionString);

        try (MongoClient mongoClient = MongoClients.create(connectionString)) {
            MongoDatabase database = mongoClient.getDatabase(dbName);
            MongoCollection<Document> usersCollection = database.getCollection(collectionName);

            System.out.println("Connected to database: " + dbName);
            System.out.println("Using collection: " + collectionName);

            System.out.println();
            System.out.println("Enter a MongoDB filter condition in JSON format.");
            System.out.println("Examples:");
            System.out.println("  {\"age\": {\"$gt\": 30}}");
            System.out.println("  {\"country\": \"USA\"}");
            System.out.println("  {\"age\": {\"$gte\": 18}, \"country\": \"Canada\"}");
            System.out.print("Filter JSON (leave empty for all users): ");

            String filterJson = scanner.nextLine().trim();

            Document filter;
            if (filterJson.isEmpty()) {
                // Empty filter = match all documents
                filter = new Document();
            } else {
                // Parse the user-provided JSON into a BSON Document
                filter = Document.parse(filterJson);
            }

            System.out.println();
            System.out.println("Running query with filter: " + filter.toJson());
            System.out.println("Matching users:");

            FindIterable<Document> results = usersCollection.find(filter);

            int count = 0;
            for (Document doc : results) {
                System.out.println(doc.toJson());
                count++;
            }

            System.out.println();
            System.out.println("Total matching users: " + count);

        } catch (Exception e) {
            System.err.println("An error occurred while querying MongoDB:");
            e.printStackTrace();
        }
    }
} {
  