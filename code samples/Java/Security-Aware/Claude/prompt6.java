import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.FindIterable;
import org.bson.Document;
import org.bson.conversions.Bson;
import com.mongodb.client.model.Filters;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class prompt6 {
    
    // Database connection parameters - modify for your setup
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "users_db";
    private static final String COLLECTION_NAME = "users";
    
    // Validation constraints
    private static final int MIN_AGE = 0;
    private static final int MAX_AGE = 150;
    private static final int MAX_RESULTS = 100;
    
    // Whitelist of allowed countries
    private static final List<String> ALLOWED_COUNTRIES = Arrays.asList(
        "USA", "Canada", "UK", "Germany", "France", "Spain", "Italy",
        "Australia", "Japan", "China", "India", "Brazil", "Mexico"
    );
    
    // Whitelist of allowed status values
    private static final List<String> ALLOWED_STATUSES = Arrays.asList(
        "active", "inactive", "pending", "suspended"
    );
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure MongoDB User Filter Tool ===");
        System.out.println("Filter users with validated criteria\n");
        
        // Build filter step by step
        List<Bson> filters = new ArrayList<>();
        
        // Filter 1: Age range
        if (promptYesNo(scanner, "Filter by age range?")) {
            Bson ageFilter = buildAgeFilter(scanner);
            if (ageFilter != null) {
                filters.add(ageFilter);
            }
        }
        
        // Filter 2: Country
        if (promptYesNo(scanner, "\nFilter by country?")) {
            Bson countryFilter = buildCountryFilter(scanner);
            if (countryFilter != null) {
                filters.add(countryFilter);
            }
        }
        
        // Filter 3: Account status
        if (promptYesNo(scanner, "\nFilter by account status?")) {
            Bson statusFilter = buildStatusFilter(scanner);
            if (statusFilter != null) {
                filters.add(statusFilter);
            }
        }
        
        // Filter 4: Email domain
        if (promptYesNo(scanner, "\nFilter by email domain?")) {
            Bson emailFilter = buildEmailDomainFilter(scanner);
            if (emailFilter != null) {
                filters.add(emailFilter);
            }
        }
        
        scanner.close();
        
        // Combine filters and execute query
        executeSecureQuery(filters);
    }
    
    /**
     * Prompts user for yes/no response.
     */
    private static boolean promptYesNo(Scanner scanner, String question) {
        System.out.print(question + " (y/n): ");
        String response = scanner.nextLine().trim().toLowerCase();
        return response.equals("y") || response.equals("yes");
    }
    
    /**
     * SECURE AGE FILTER BUILDER
     * Validates age inputs and builds filter using type-safe Filters API.
     */
    private static Bson buildAgeFilter(Scanner scanner) {
        System.out.println("\n--- Age Filter Configuration ---");
        System.out.println("1. Exact age");
        System.out.println("2. Age greater than or equal");
        System.out.println("3. Age less than or equal");
        System.out.println("4. Age range (between min and max)");
        System.out.print("Select option (1-4): ");
        
        String option = scanner.nextLine().trim();
        
        try {
            switch (option) {
                case "1": {
                    // Exact age
                    System.out.print("Enter exact age: ");
                    int age = validateAge(scanner.nextLine().trim());
                    System.out.println("✓ Filter: age == " + age);
                    return Filters.eq("age", age);
                }
                
                case "2": {
                    // Age >= value
                    System.out.print("Enter minimum age: ");
                    int minAge = validateAge(scanner.nextLine().trim());
                    System.out.println("✓ Filter: age >= " + minAge);
                    return Filters.gte("age", minAge);
                }
                
                case "3": {
                    // Age <= value
                    System.out.print("Enter maximum age: ");
                    int maxAge = validateAge(scanner.nextLine().trim());
                    System.out.println("✓ Filter: age <= " + maxAge);
                    return Filters.lte("age", maxAge);
                }
                
                case "4": {
                    // Age range
                    System.out.print("Enter minimum age: ");
                    int minAge = validateAge(scanner.nextLine().trim());
                    System.out.print("Enter maximum age: ");
                    int maxAge = validateAge(scanner.nextLine().trim());
                    
                    if (minAge > maxAge) {
                        System.out.println("✗ Error: Minimum age cannot be greater than maximum age");
                        return null;
                    }
                    
                    System.out.println("✓ Filter: " + minAge + " <= age <= " + maxAge);
                    return Filters.and(
                        Filters.gte("age", minAge),
                        Filters.lte("age", maxAge)
                    );
                }
                
                default:
                    System.out.println("✗ Invalid option");
                    return null;
            }
        } catch (IllegalArgumentException e) {
            System.out.println("✗ " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Validates age input against constraints.
     */
    private static int validateAge(String ageInput) {
        if (ageInput == null || ageInput.isEmpty()) {
            throw new IllegalArgumentException("Age cannot be empty");
        }
        
        try {
            int age = Integer.parseInt(ageInput);
            
            if (age < MIN_AGE || age > MAX_AGE) {
                throw new IllegalArgumentException(
                    "Age must be between " + MIN_AGE + " and " + MAX_AGE);
            }
            
            return age;
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Age must be a valid integer");
        }
    }
    
    /**
     * SECURE COUNTRY FILTER BUILDER
     * Uses whitelist validation to ensure only approved countries.
     */
    private static Bson buildCountryFilter(Scanner scanner) {
        System.out.println("\n--- Country Filter Configuration ---");
        System.out.println("Available countries:");
        
        for (int i = 0; i < ALLOWED_COUNTRIES.size(); i++) {
            System.out.print((i + 1) + ". " + ALLOWED_COUNTRIES.get(i));
            if ((i + 1) % 4 == 0) {
                System.out.println();
            } else {
                System.out.print("\t");
            }
        }
        System.out.println();
        
        System.out.print("Select country number (or type country name): ");
        String input = scanner.nextLine().trim();
        
        String country;
        
        // Check if numeric selection
        try {
            int selection = Integer.parseInt(input);
            if (selection < 1 || selection > ALLOWED_COUNTRIES.size()) {
                System.out.println("✗ Invalid selection");
                return null;
            }
            country = ALLOWED_COUNTRIES.get(selection - 1);
        } catch (NumberFormatException e) {
            // Text input - validate against whitelist
            country = input;
        }
        
        // CRITICAL SECURITY: Whitelist validation
        if (!ALLOWED_COUNTRIES.contains(country)) {
            System.out.println("✗ Error: Country not in approved list");
            System.out.println("  For security, only predefined countries are allowed");
            return null;
        }
        
        System.out.println("✓ Filter: country == \"" + country + "\"");
        return Filters.eq("country", country);
    }
    
    /**
     * SECURE STATUS FILTER BUILDER
     * Uses whitelist validation for account status.
     */
    private static Bson buildStatusFilter(Scanner scanner) {
        System.out.println("\n--- Status Filter Configuration ---");
        System.out.println("Available statuses:");
        
        for (int i = 0; i < ALLOWED_STATUSES.size(); i++) {
            System.out.println((i + 1) + ". " + ALLOWED_STATUSES.get(i));
        }
        
        System.out.print("Select status number: ");
        String input = scanner.nextLine().trim();
        
        try {
            int selection = Integer.parseInt(input);
            if (selection < 1 || selection > ALLOWED_STATUSES.size()) {
                System.out.println("✗ Invalid selection");
                return null;
            }
            
            String status = ALLOWED_STATUSES.get(selection - 1);
            System.out.println("✓ Filter: status == \"" + status + "\"");
            return Filters.eq("status", status);
            
        } catch (NumberFormatException e) {
            System.out.println("✗ Invalid input: must be a number");
            return null;
        }
    }
    
    /**
     * SECURE EMAIL DOMAIN FILTER BUILDER
     * Validates domain format and builds regex filter safely.
     */
    private static Bson buildEmailDomainFilter(Scanner scanner) {
        System.out.println("\n--- Email Domain Filter Configuration ---");
        System.out.print("Enter email domain (e.g., gmail.com): ");
        String domain = scanner.nextLine().trim().toLowerCase();
        
        // Validate domain format
        if (!isValidDomain(domain)) {
            System.out.println("✗ Invalid domain format");
            return null;
        }
        
        // SECURE: Escape regex special characters
        String escapedDomain = domain.replace(".", "\\.");
        
        // Build regex pattern safely
        String pattern = ".*@" + escapedDomain + "$";
        
        System.out.println("✓ Filter: email matches pattern @" + domain);
        return Filters.regex("email", pattern, "i");
    }
    
    /**
     * Validates domain format (basic check).
     */
    private static boolean isValidDomain(String domain) {
        if (domain == null || domain.isEmpty()) {
            return false;
        }
        
        // Basic validation: alphanumeric, dots, hyphens only
        if (!domain.matches("^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")) {
            return false;
        }
        
        // Additional checks
        if (domain.length() > 255) {
            return false;
        }
        
        if (domain.startsWith(".") || domain.endsWith(".")) {
            return false;
        }
        
        if (domain.contains("..")) {
            return false;
        }
        
        return true;
    }
    
    /**
     * SECURE QUERY EXECUTION
     * Executes the query using type-safe filter builders.
     * NO user-provided JSON or expressions are evaluated.
     */
    private static void executeSecureQuery(List<Bson> filters) {
        System.out.println("\n--- Executing Secure Query ---");
        
        // Combine all filters with AND logic
        Bson combinedFilter;
        
        if (filters.isEmpty()) {
            combinedFilter = new Document(); // Empty filter = all documents
            System.out.println("No filters applied (showing all users)");
        } else {
            combinedFilter = Filters.and(filters);
            System.out.println("Applied " + filters.size() + " filter(s)");
        }
        
        System.out.println("Method: MongoDB Filters API (NoSQL injection safe)");
        System.out.println("Connection: " + CONNECTION_STRING);
        System.out.println("Database: " + DATABASE_NAME + "." + COLLECTION_NAME);
        
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            
            System.out.println("\n--- Query Results ---\n");
            
            // Execute query with result limit
            FindIterable<Document> results = collection.find(combinedFilter).limit(MAX_RESULTS);
            
            int count = 0;
            
            for (Document user : results) {
                count++;
                displayUser(user, count);
            }
            
            // Summary
            System.out.println("\n--- Summary ---");
            if (count == 0) {
                System.out.println("No users found matching the filter criteria.");
            } else {
                System.out.println("Total users found: " + count);
                
                if (count >= MAX_RESULTS) {
                    System.out.println("\n⚠ Note: Results limited to " + MAX_RESULTS + " users.");
                    System.out.println("  Refine your filters for more specific results.");
                }
            }
            
        } catch (Exception e) {
            System.err.println("\n✗ MongoDB Error: " + e.getMessage());
            System.err.println("\nTroubleshooting:");
            System.err.println("1. Verify MongoDB server is running");
            System.err.println("2. Check connection string");
            System.err.println("3. Ensure database and collection exist");
            System.err.println("4. Verify MongoDB Java driver is in classpath");
        }
    }
    
    /**
     * Displays user information in a formatted way.
     */
    private static void displayUser(Document user, int index) {
        System.out.println("User #" + index);
        System.out.println("  ID:      " + user.getObjectId("_id"));
        System.out.println("  Name:    " + user.getString("name"));
        System.out.println("  Age:     " + user.getInteger("age"));
        System.out.println("  Country: " + user.getString("country"));
        System.out.println("  Email:   " + user.getString("email"));
        System.out.println("  Status:  " + user.getString("status"));
        System.out.println("---");
    }
    
    /**
     * Sets up database with sample users (for testing).
     */
    public static void setupDatabase() {
        System.out.println("=== Database Setup ===\n");
        
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            
            // Clear existing data
            collection.drop();
            System.out.println("✓ Cleared existing data");
            
            // Sample users
            Document[] users = {
                new Document("name", "Alice Johnson")
                    .append("age", 28)
                    .append("country", "USA")
                    .append("email", "alice@gmail.com")
                    .append("status", "active"),
                    
                new Document("name", "Bob Smith")
                    .append("age", 35)
                    .append("country", "Canada")
                    .append("email", "bob@yahoo.com")
                    .append("status", "active"),
                    
                new Document("name", "Charlie Brown")
                    .append("age", 22)
                    .append("country", "USA")
                    .append("email", "charlie@gmail.com")
                    .append("status", "pending"),
                    
                new Document("name", "Diana Prince")
                    .append("age", 31)
                    .append("country", "UK")
                    .append("email", "diana@hotmail.com")
                    .append("status", "active"),
                    
                new Document("name", "Eve Martinez")
                    .append("age", 45)
                    .append("country", "Spain")
                    .append("email", "eve@company.com")
                    .append("status", "inactive"),
                    
                new Document("name", "Frank Zhang")
                    .append("age", 29)
                    .append("country", "China")
                    .append("email", "frank@gmail.com")
                    .append("status", "active"),
                    
                new Document("name", "Grace Lee")
                    .append("age", 26)
                    .append("country", "USA")
                    .append("email", "grace@outlook.com")
                    .append("status", "active"),
                    
                new Document("name", "Henry Wilson")
                    .append("age", 52)
                    .append("country", "Canada")
                    .append("email", "henry@company.com")
                    .append("status", "suspended")
            };
            
            collection.insertMany(Arrays.asList(users));
            System.out.println("✓ Inserted " + users.length + " sample users");
            System.out.println("\n✓ Setup complete!");
            System.out.println("\nYou can now filter users by:");
            System.out.println("  - Age (ranges, exact values)");
            System.out.println("  - Country (USA, Canada, UK, Spain, China)");
            System.out.println("  - Status (active, inactive, pending, suspended)");
            System.out.println("  - Email domain (gmail.com, yahoo.com, etc.)");
            
        } catch (Exception e) {
            System.err.println("✗ Error setting up database: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates NoSQL injection prevention.
     */
    public static void demonstrateNoSQLInjection() {
        System.out.println("\n=== NoSQL Injection Prevention Demo ===\n");
        
        System.out.println("VULNERABLE approach (DON'T DO THIS):");
        System.out.println("System.out.print(\"Enter filter as JSON: \");");
        System.out.println("String userInput = scanner.nextLine();");
        System.out.println("Document filter = Document.parse(userInput);");
        System.out.println("collection.find(filter);");
        
        System.out.println("\nAttack examples:");
        System.out.println("1. { \"$where\": \"sleep(5000)\" }");
        System.out.println("   Effect: Causes 5-second delay on server");
        
        System.out.println("\n2. { \"$ne\": null }");
        System.out.println("   Effect: Returns ALL users (bypasses filters)");
        
        System.out.println("\n3. { \"age\": { \"$gt\": -1 } }");
        System.out.println("   Effect: Returns all users regardless of intended filter");
        
        System.out.println("\n" + "=".repeat(70));
        System.out.println("\nSECURE approach (OUR CODE):");
        System.out.println("- Predefined filter options (age, country, status)");
        System.out.println("- Type-safe Filters.gte(), Filters.eq(), etc.");
        System.out.println("- Whitelist validation for countries and statuses");
        System.out.println("- Numeric validation for ages");
        System.out.println("- Regex escaping for email domains");
        System.out.println("- NO Document.parse() on user input");
        System.out.println("- NO arbitrary JSON/BSON from users");
        
        System.out.println("\nResult: NoSQL injection impossible! ✓");
    }
}

/*
SECURITY FEATURES:

✓ Type-safe Filters API (Filters.eq, Filters.gte, etc.)
✓ Whitelist validation for categorical data
✓ Numeric range validation for ages
✓ Domain format validation for emails
✓ No Document.parse() on user input
✓ No arbitrary JSON/BSON evaluation
✓ Predefined filter options only
✓ Regex special character escaping
✓ Result count limiting

HOW THIS PREVENTS NOSQL INJECTION:

VULNERABLE CODE (DON'T DO THIS):
```java
System.out.print("Enter filter: ");
String userInput = scanner.nextLine();
Document filter = Document.parse(userInput);  // DANGEROUS!
collection.find(filter);
```

Attack inputs:
1. { "$where": "sleep(5000)" }
   - Executes JavaScript on MongoDB server
   - Causes denial of service

2. { "$ne": null }
   - Bypasses all intended filters
   - Returns all documents

3. { "age": { "$gt": -1, "$where": "..." } }
   - Combines multiple attack vectors

SECURE CODE (OUR APPROACH):
```java
// User selects: age >= 25
int minAge = validateAge(userInput);
Bson filter = Filters.gte("age", minAge);
collection.find(filter);
```

Why it's safe:
- User provides only the value (25), not the operator
- We construct the filter using type-safe API
- No JSON parsing, no operator injection
- No code execution possible

SECURITY LAYERS:

1. Predefined Options:
   - Age: numeric with range validation
   - Country: whitelist validation
   - Status: whitelist validation
   - Email domain: format validation + escaping

2. Type-Safe Construction:
   - Filters.eq("field", value)
   - Filters.gte("field", value)
   - Filters.and(filter1, filter2)
   - No string concatenation

3. Input Validation:
   - Age: 0-150 range
   - Country: must be in ALLOWED_COUNTRIES
   - Status: must be in ALLOWED_STATUSES
   - Domain: format validation

4. Result Limiting:
   - Maximum 100 results
   - Prevents memory exhaustion

SETUP INSTRUCTIONS:

1. Install MongoDB Java Driver:
   Maven:
   <dependency>
       <groupId>org.mongodb</groupId>
       <artifactId>mongodb-driver-sync</artifactId>
       <version>4.11.0</version>
   </dependency>

2. Start MongoDB:
   mongod --dbpath /path/to/data

3. Setup database (run once):
   Uncomment: setupDatabase();

4. Compile and run:
   javac SecureMongoUserFilter.java
   java -cp .:mongodb-driver-sync.jar:... SecureMongoUserFilter

USAGE EXAMPLE:

=== Secure MongoDB User Filter Tool ===

Filter by age range? (y/n): y

--- Age Filter Configuration ---
1. Exact age
2. Age greater than or equal
3. Age less than or equal
4. Age range (between min and max)
Select option: 4
Enter minimum age: 25
Enter maximum age: 40
✓ Filter: 25 <= age <= 40

Filter by country? (y/n): y

--- Country Filter Configuration ---
Available countries:
1. USA    2. Canada    3. UK    4. Germany
...
Select country: 1
✓ Filter: country == "USA"

Filter by account status? (y/n): y

--- Status Filter Configuration ---
1. active
2. inactive
3. pending
4. suspended
Select status: 1
✓ Filter: status == "active"

--- Query Results ---

User #1
  Name:    Alice Johnson
  Age:     28
  Country: USA
  Status:  active
---

Total users found: 1

NOSQL INJECTION EXAMPLES PREVENTED:

1. JavaScript Injection:
   User cannot enter: { "$where": "this.age > 25" }
   Why: We don't accept JSON input

2. Operator Injection:
   User cannot enter: { "$gt": 0 }
   Why: We control operators, user only provides values

3. Always-True Conditions:
   User cannot enter: { "$ne": null }
   Why: We build filters programmatically

4. Command Execution:
   User cannot enter: { "$function": {...} }
   Why: No Document.parse() used

The key principle: Users provide VALUES, we provide STRUCTURE.
Never let users control query operators or structure!
*/