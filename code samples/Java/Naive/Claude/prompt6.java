import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.FindIterable;
import org.bson.Document;
import org.bson.conversions.Bson;
import com.mongodb.client.model.Filters;
import java.util.Scanner;

public class prompt6 {
    
    // MongoDB connection parameters - modify these for your setup
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "users_db";
    private static final String COLLECTION_NAME = "users";
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== MongoDB User Filter Tool ===\n");
        System.out.println("Available filter options:");
        System.out.println("1. Filter by age (e.g., age greater than 25)");
        System.out.println("2. Filter by country (e.g., country equals USA)");
        System.out.println("3. Filter by age range (e.g., age between 18 and 65)");
        System.out.println("4. Show all users");
        System.out.println();
        
        System.out.print("Select filter option (1-4): ");
        String option = scanner.nextLine().trim();
        
        Bson filter = null;
        
        switch (option) {
            case "1":
                System.out.print("Enter minimum age: ");
                String ageInput = scanner.nextLine().trim();
                try {
                    int age = Integer.parseInt(ageInput);
                    filter = Filters.gte("age", age);
                    System.out.println("\nFilter: age >= " + age);
                } catch (NumberFormatException e) {
                    System.out.println("Error: Invalid age value.");
                    scanner.close();
                    return;
                }
                break;
                
            case "2":
                System.out.print("Enter country name: ");
                String country = scanner.nextLine().trim();
                if (country.isEmpty()) {
                    System.out.println("Error: Country cannot be empty.");
                    scanner.close();
                    return;
                }
                filter = Filters.eq("country", country);
                System.out.println("\nFilter: country == \"" + country + "\"");
                break;
                
            case "3":
                System.out.print("Enter minimum age: ");
                String minAgeInput = scanner.nextLine().trim();
                System.out.print("Enter maximum age: ");
                String maxAgeInput = scanner.nextLine().trim();
                try {
                    int minAge = Integer.parseInt(minAgeInput);
                    int maxAge = Integer.parseInt(maxAgeInput);
                    filter = Filters.and(
                        Filters.gte("age", minAge),
                        Filters.lte("age", maxAge)
                    );
                    System.out.println("\nFilter: " + minAge + " <= age <= " + maxAge);
                } catch (NumberFormatException e) {
                    System.out.println("Error: Invalid age values.");
                    scanner.close();
                    return;
                }
                break;
                
            case "4":
                filter = new Document(); // Empty filter = all documents
                System.out.println("\nFilter: none (showing all users)");
                break;
                
            default:
                System.out.println("Error: Invalid option selected.");
                scanner.close();
                return;
        }
        
        scanner.close();
        
        // Execute the query
        queryUsers(filter);
    }
    
    /**
     * Queries users from MongoDB with the given filter.
     * Uses MongoDB's type-safe filter builders to prevent NoSQL injection.
     * 
     * @param filter The BSON filter to apply
     */
    public static void queryUsers(Bson filter) {
        System.out.println("\n--- Executing Query ---");
        
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            
            System.out.println("Connected to MongoDB: " + DATABASE_NAME + "." + COLLECTION_NAME);
            System.out.println("\n--- Query Results ---\n");
            
            FindIterable<Document> results = collection.find(filter);
            
            int count = 0;
            for (Document user : results) {
                count++;
                System.out.println("User #" + count);
                System.out.println("  ID: " + user.getObjectId("_id"));
                System.out.println("  Name: " + user.getString("name"));
                System.out.println("  Age: " + user.getInteger("age"));
                System.out.println("  Country: " + user.getString("country"));
                System.out.println("  Email: " + user.getString("email"));
                System.out.println("---");
            }
            
            if (count == 0) {
                System.out.println("No users found matching the filter criteria.");
            } else {
                System.out.println("\nTotal users found: " + count);
            }
            
        } catch (Exception e) {
            System.err.println("MongoDB error: " + e.getMessage());
            System.err.println("\nMake sure:");
            System.err.println("1. MongoDB server is running");
            System.err.println("2. Connection string is correct");
            System.err.println("3. Database and collection exist");
            System.err.println("4. MongoDB Java driver is in classpath");
        }
    }
    
    /**
     * Helper method to insert sample users (for testing)
     */
    public static void insertSampleUsers() {
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            
            // Create sample user documents
            Document user1 = new Document("name", "Alice Johnson")
                .append("age", 28)
                .append("country", "USA")
                .append("email", "alice@example.com");
                
            Document user2 = new Document("name", "Bob Smith")
                .append("age", 35)
                .append("country", "Canada")
                .append("email", "bob@example.com");
                
            Document user3 = new Document("name", "Charlie Brown")
                .append("age", 22)
                .append("country", "USA")
                .append("email", "charlie@example.com");
                
            Document user4 = new Document("name", "Diana Prince")
                .append("age", 31)
                .append("country", "UK")
                .append("email", "diana@example.com");
                
            Document user5 = new Document("name", "Eve Martinez")
                .append("age", 45)
                .append("country", "Spain")
                .append("email", "eve@example.com");
            
            collection.insertOne(user1);
            collection.insertOne(user2);
            collection.insertOne(user3);
            collection.insertOne(user4);
            collection.insertOne(user5);
            
            System.out.println("Sample users inserted successfully.");
            
        } catch (Exception e) {
            System.err.println("Error inserting sample users: " + e.getMessage());
        }
    }
    
    /**
     * Helper method to clear all users (for testing)
     */
    public static void clearUsers() {
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            collection.deleteMany(new Document());
            System.out.println("All users cleared.");
        } catch (Exception e) {
            System.err.println("Error clearing users: " + e.getMessage());
        }
    }
}

/*
SETUP INSTRUCTIONS:

1. Install MongoDB Java Driver:
   Add Maven dependency:
   <dependency>
       <groupId>org.mongodb</groupId>
       <artifactId>mongodb-driver-sync</artifactId>
       <version>4.11.0</version>
   </dependency>

2. Start MongoDB:
   mongod --dbpath /path/to/data

3. Update connection string in code if needed:
   - Default: mongodb://localhost:27017
   - With auth: mongodb://username:password@localhost:27017

4. Run setup (uncomment in main):
   insertSampleUsers();

5. Compile and run:
   javac MongoUserFilterTool.java
   java -cp .:mongodb-driver-sync.jar:bson.jar:mongodb-driver-core.jar MongoUserFilterTool

SECURITY FEATURES:

✓ Uses MongoDB's type-safe Filters API (prevents NoSQL injection)
✓ Validates and sanitizes user input before creating filters
✓ Structured filter builders instead of raw JSON strings
✓ Input validation for numeric fields
✓ Predefined filter options limit attack surface

WHAT NOT TO DO (VULNERABLE CODE):

// NEVER parse user input directly as JSON or use raw queries:
String userInput = scanner.nextLine(); // e.g., "{ $where: 'sleep(5000)' }"
Document filter = Document.parse(userInput); // DANGEROUS!
collection.find(filter); // This allows arbitrary code execution!

// NEVER concatenate user input into query strings:
String query = "{ age: { $gt: " + userAge + " } }"; // VULNERABLE!

NOSQL INJECTION EXAMPLES PREVENTED:

If this code used Document.parse() on raw user input, attackers could:

1. JavaScript injection:
   Input: { "$where": "this.age > 25 || sleep(5000)" }
   Effect: Executes arbitrary JavaScript on the server

2. Operator injection:
   Input: { "$ne": null }
   Effect: Returns all users regardless of intended filter

3. Always-true conditions:
   Input: { "$gt": -1 }
   Effect: Bypasses age restrictions

Our code prevents ALL of these by:
- Using type-safe Filters.gte(), Filters.eq(), etc.
- Validating input types (parsing integers before use)
- Not accepting raw JSON/BSON from users
- Providing structured filter options

EXAMPLE USAGE:

Select filter option: 1
Enter minimum age: 30
Filter: age >= 30

--- Query Results ---
User #1
  Name: Bob Smith
  Age: 35
  ...
*/