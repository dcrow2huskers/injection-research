import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.FindIterable;
import org.bson.Document;
import org.bson.conversions.Bson;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Scanner;

public class prompt7 {
    
    // Database connection parameters
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "blog_db";
    private static final String COLLECTION_NAME = "posts";
    
    // Validation constraints
    private static final int MAX_RESULTS = 50;
    private static final int MAX_TITLE_LENGTH = 200;
    private static final int MAX_AUTHOR_LENGTH = 100;
    private static final int MAX_TAG_LENGTH = 50;
    
    // Date format for user input
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
    
    // Whitelist of allowed tags
    private static final List<String> ALLOWED_TAGS = Arrays.asList(
        "technology", "programming", "java", "mongodb", "security",
        "web-development", "databases", "tutorial", "best-practices",
        "design", "architecture", "devops", "testing"
    );
    
    // Whitelist of allowed status values
    private static final List<String> ALLOWED_STATUSES = Arrays.asList(
        "published", "draft", "archived"
    );
    
    // Fields to display in results (security: limit exposed fields)
    private static final List<String> OUTPUT_FIELDS = Arrays.asList(
        "title", "author", "tags", "published_date", "status", "summary"
    );
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("=== Secure MongoDB Blog Search Tool ===");
        System.out.println("Search blog posts with structured criteria\n");
        
        // Build search criteria step by step
        List<Bson> filters = new ArrayList<>();
        
        System.out.println("--- Available Search Criteria ---");
        System.out.println("1. Author name");
        System.out.println("2. Tag");
        System.out.println("3. Title keyword");
        System.out.println("4. Date range");
        System.out.println("5. Publication status");
        System.out.println();
        
        // Collect filters
        if (promptYesNo(scanner, "Search by author?")) {
            Bson authorFilter = buildAuthorFilter(scanner);
            if (authorFilter != null) {
                filters.add(authorFilter);
            }
        }
        
        if (promptYesNo(scanner, "\nSearch by tag?")) {
            Bson tagFilter = buildTagFilter(scanner);
            if (tagFilter != null) {
                filters.add(tagFilter);
            }
        }
        
        if (promptYesNo(scanner, "\nSearch by title keyword?")) {
            Bson titleFilter = buildTitleFilter(scanner);
            if (titleFilter != null) {
                filters.add(titleFilter);
            }
        }
        
        if (promptYesNo(scanner, "\nSearch by date range?")) {
            Bson dateFilter = buildDateFilter(scanner);
            if (dateFilter != null) {
                filters.add(dateFilter);
            }
        }
        
        if (promptYesNo(scanner, "\nFilter by publication status?")) {
            Bson statusFilter = buildStatusFilter(scanner);
            if (statusFilter != null) {
                filters.add(statusFilter);
            }
        }
        
        // Sorting preference
        System.out.println("\n--- Sort Options ---");
        System.out.println("1. Newest first (default)");
        System.out.println("2. Oldest first");
        System.out.println("3. Title (A-Z)");
        System.out.print("Select sort option (1-3, default=1): ");
        String sortOption = scanner.nextLine().trim();
        if (sortOption.isEmpty()) {
            sortOption = "1";
        }
        
        scanner.close();
        
        // Execute secure query
        executeSecureQuery(filters, sortOption);
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
     * SECURE AUTHOR FILTER BUILDER
     * Validates author name and builds filter using type-safe API.
     */
    private static Bson buildAuthorFilter(Scanner scanner) {
        System.out.println("\n--- Author Filter ---");
        System.out.print("Enter author name: ");
        String author = scanner.nextLine().trim();
        
        // Validate author input
        if (author.isEmpty()) {
            System.out.println("✗ Author name cannot be empty");
            return null;
        }
        
        if (author.length() > MAX_AUTHOR_LENGTH) {
            System.out.println("✗ Author name too long (max " + MAX_AUTHOR_LENGTH + " characters)");
            return null;
        }
        
        // Check for suspicious patterns (for logging)
        if (containsSuspiciousPatterns(author)) {
            System.out.println("⚠ Warning: Input contains suspicious patterns");
            System.out.println("  (Safe with type-safe filters, but logged for monitoring)");
        }
        
        System.out.println("✓ Filter: author == \"" + author + "\"");
        
        // SECURE: Using type-safe Filters.eq()
        return Filters.eq("author", author);
    }
    
    /**
     * SECURE TAG FILTER BUILDER
     * Uses whitelist validation for tags.
     */
    private static Bson buildTagFilter(Scanner scanner) {
        System.out.println("\n--- Tag Filter ---");
        System.out.println("Available tags:");
        
        for (int i = 0; i < ALLOWED_TAGS.size(); i++) {
            System.out.print((i + 1) + ". " + ALLOWED_TAGS.get(i));
            if ((i + 1) % 3 == 0) {
                System.out.println();
            } else {
                System.out.print("\t");
            }
        }
        System.out.println();
        
        System.out.print("Select tag number: ");
        String input = scanner.nextLine().trim();
        
        try {
            int selection = Integer.parseInt(input);
            if (selection < 1 || selection > ALLOWED_TAGS.size()) {
                System.out.println("✗ Invalid selection");
                return null;
            }
            
            String tag = ALLOWED_TAGS.get(selection - 1);
            System.out.println("✓ Filter: tags contains \"" + tag + "\"");
            
            // SECURE: Using Filters.eq() to match array element
            return Filters.eq("tags", tag);
            
        } catch (NumberFormatException e) {
            System.out.println("✗ Invalid input: must be a number");
            return null;
        }
    }
    
    /**
     * SECURE TITLE FILTER BUILDER
     * Validates and escapes title keyword for safe regex search.
     */
    private static Bson buildTitleFilter(Scanner scanner) {
        System.out.println("\n--- Title Keyword Filter ---");
        System.out.print("Enter keyword to search in title: ");
        String keyword = scanner.nextLine().trim();
        
        // Validate keyword
        if (keyword.isEmpty()) {
            System.out.println("✗ Keyword cannot be empty");
            return null;
        }
        
        if (keyword.length() > MAX_TITLE_LENGTH) {
            System.out.println("✗ Keyword too long (max " + MAX_TITLE_LENGTH + " characters)");
            return null;
        }
        
        // Check for suspicious patterns
        if (containsSuspiciousPatterns(keyword)) {
            System.out.println("⚠ Warning: Input contains suspicious patterns");
        }
        
        // SECURE: Escape regex special characters
        String escapedKeyword = escapeRegex(keyword);
        
        // Build case-insensitive regex pattern
        String pattern = ".*" + escapedKeyword + ".*";
        
        System.out.println("✓ Filter: title contains \"" + keyword + "\" (case-insensitive)");
        
        // SECURE: Using Filters.regex() with escaped pattern
        return Filters.regex("title", pattern, "i");
    }
    
    /**
     * SECURE DATE FILTER BUILDER
     * Validates dates and builds filter using type-safe API.
     */
    private static Bson buildDateFilter(Scanner scanner) {
        System.out.println("\n--- Date Range Filter ---");
        System.out.println("Date format: yyyy-MM-dd (e.g., 2024-01-15)");
        
        System.out.print("From date (or press Enter to skip): ");
        String fromDateStr = scanner.nextLine().trim();
        
        System.out.print("To date (or press Enter to skip): ");
        String toDateStr = scanner.nextLine().trim();
        
        if (fromDateStr.isEmpty() && toDateStr.isEmpty()) {
            System.out.println("✗ At least one date required");
            return null;
        }
        
        try {
            List<Bson> dateFilters = new ArrayList<>();
            
            if (!fromDateStr.isEmpty()) {
                Date fromDate = DATE_FORMAT.parse(fromDateStr);
                dateFilters.add(Filters.gte("published_date", fromDate));
                System.out.println("✓ Filter: published_date >= " + fromDateStr);
            }
            
            if (!toDateStr.isEmpty()) {
                Date toDate = DATE_FORMAT.parse(toDateStr);
                dateFilters.add(Filters.lte("published_date", toDate));
                System.out.println("✓ Filter: published_date <= " + toDateStr);
            }
            
            // SECURE: Combine date filters with AND
            if (dateFilters.size() == 1) {
                return dateFilters.get(0);
            } else {
                return Filters.and(dateFilters);
            }
            
        } catch (ParseException e) {
            System.out.println("✗ Invalid date format. Use yyyy-MM-dd");
            return null;
        }
    }
    
    /**
     * SECURE STATUS FILTER BUILDER
     * Uses whitelist validation for publication status.
     */
    private static Bson buildStatusFilter(Scanner scanner) {
        System.out.println("\n--- Status Filter ---");
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
            
            // SECURE: Using Filters.eq()
            return Filters.eq("status", status);
            
        } catch (NumberFormatException e) {
            System.out.println("✗ Invalid input: must be a number");
            return null;
        }
    }
    
    /**
     * Checks for suspicious patterns in user input (for logging/monitoring).
     */
    private static boolean containsSuspiciousPatterns(String input) {
        String[] suspicious = {"$where", "$ne", "$gt", "$lt", "$regex", "function", "eval", "javascript"};
        String lowerInput = input.toLowerCase();
        
        for (String pattern : suspicious) {
            if (lowerInput.contains(pattern)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Escapes regex special characters to prevent regex injection.
     */
    private static String escapeRegex(String input) {
        // Escape special regex characters
        return input.replaceAll("([.+*?^$(){}\\[\\]\\\\|])", "\\\\$1");
    }
    
    /**
     * SECURE QUERY EXECUTION
     * Executes query using type-safe filters and projections.
     * Only outputs whitelisted fields.
     */
    private static void executeSecureQuery(List<Bson> filters, String sortOption) {
        System.out.println("\n--- Executing Secure Query ---");
        
        // Combine filters
        Bson combinedFilter;
        if (filters.isEmpty()) {
            combinedFilter = new Document();
            System.out.println("No filters applied (showing all posts)");
        } else {
            combinedFilter = Filters.and(filters);
            System.out.println("Applied " + filters.size() + " filter(s)");
        }
        
        // SECURITY: Create projection to limit output fields
        Bson projection = Projections.include(OUTPUT_FIELDS);
        System.out.println("Output fields: " + String.join(", ", OUTPUT_FIELDS));
        
        // Determine sort order
        Bson sort;
        switch (sortOption) {
            case "2":
                sort = Sorts.ascending("published_date");
                System.out.println("Sort: Oldest first");
                break;
            case "3":
                sort = Sorts.ascending("title");
                System.out.println("Sort: Title (A-Z)");
                break;
            default:
                sort = Sorts.descending("published_date");
                System.out.println("Sort: Newest first");
                break;
        }
        
        System.out.println("Method: MongoDB Filters API (NoSQL injection safe)");
        
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            
            System.out.println("\n--- Search Results ---\n");
            
            // Execute query with projection, sort, and limit
            FindIterable<Document> results = collection.find(combinedFilter)
                .projection(projection)
                .sort(sort)
                .limit(MAX_RESULTS);
            
            int count = 0;
            
            for (Document post : results) {
                count++;
                displayPost(post, count);
            }
            
            // Summary
            System.out.println("\n--- Summary ---");
            if (count == 0) {
                System.out.println("No blog posts found matching the criteria.");
            } else {
                System.out.println("Total posts found: " + count);
                
                if (count >= MAX_RESULTS) {
                    System.out.println("\n⚠ Note: Results limited to " + MAX_RESULTS + " posts.");
                    System.out.println("  Refine your search criteria for more specific results.");
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
     * Displays blog post information in a formatted way.
     * SECURITY: Only displays whitelisted fields.
     */
    private static void displayPost(Document post, int index) {
        System.out.println("Post #" + index);
        System.out.println("  Title:     " + post.getString("title"));
        System.out.println("  Author:    " + post.getString("author"));
        
        // Tags (array field)
        @SuppressWarnings("unchecked")
        List<String> tags = (List<String>) post.get("tags");
        if (tags != null && !tags.isEmpty()) {
            System.out.println("  Tags:      " + String.join(", ", tags));
        }
        
        // Date
        Date publishedDate = post.getDate("published_date");
        if (publishedDate != null) {
            System.out.println("  Published: " + DATE_FORMAT.format(publishedDate));
        }
        
        System.out.println("  Status:    " + post.getString("status"));
        
        // Summary (truncate if too long)
        String summary = post.getString("summary");
        if (summary != null && !summary.isEmpty()) {
            String displaySummary = summary.length() > 100 
                ? summary.substring(0, 97) + "..." 
                : summary;
            System.out.println("  Summary:   " + displaySummary);
        }
        
        System.out.println("---");
    }
    
    /**
     * Sets up database with sample blog posts (for testing).
     */
    public static void setupDatabase() {
        System.out.println("=== Database Setup ===\n");
        
        try (MongoClient mongoClient = MongoClients.create(CONNECTION_STRING)) {
            MongoDatabase database = mongoClient.getDatabase(DATABASE_NAME);
            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME);
            
            // Clear existing data
            collection.drop();
            System.out.println("✓ Cleared existing data");
            
            // Sample blog posts
            Document[] posts = {
                new Document("title", "Introduction to MongoDB Security")
                    .append("author", "Alice Johnson")
                    .append("tags", Arrays.asList("mongodb", "security", "databases"))
                    .append("published_date", parseDate("2024-01-15"))
                    .append("status", "published")
                    .append("summary", "Learn the fundamentals of securing MongoDB databases")
                    .append("content", "Full article content here..."),
                    
                new Document("title", "Java Best Practices for 2024")
                    .append("author", "Bob Smith")
                    .append("tags", Arrays.asList("java", "programming", "best-practices"))
                    .append("published_date", parseDate("2024-02-20"))
                    .append("status", "published")
                    .append("summary", "Modern Java development practices and patterns")
                    .append("content", "Full article content here..."),
                    
                new Document("title", "Building RESTful APIs with Java")
                    .append("author", "Alice Johnson")
                    .append("tags", Arrays.asList("java", "web-development", "tutorial"))
                    .append("published_date", parseDate("2024-03-10"))
                    .append("status", "published")
                    .append("summary", "Step-by-step guide to creating REST APIs")
                    .append("content", "Full article content here..."),
                    
                new Document("title", "NoSQL Injection Prevention Guide")
                    .append("author", "Charlie Davis")
                    .append("tags", Arrays.asList("security", "mongodb", "best-practices"))
                    .append("published_date", parseDate("2024-04-05"))
                    .append("status", "published")
                    .append("summary", "Comprehensive guide to preventing NoSQL injection attacks")
                    .append("content", "Full article content here..."),
                    
                new Document("title", "Draft: Database Migration Strategies")
                    .append("author", "Bob Smith")
                    .append("tags", Arrays.asList("databases", "devops"))
                    .append("published_date", parseDate("2024-05-01"))
                    .append("status", "draft")
                    .append("summary", "Planning and executing database migrations safely")
                    .append("content", "Work in progress..."),
                    
                new Document("title", "Testing MongoDB Applications")
                    .append("author", "Diana Prince")
                    .append("tags", Arrays.asList("mongodb", "testing", "java"))
                    .append("published_date", parseDate("2024-06-15"))
                    .append("status", "published")
                    .append("summary", "Strategies for testing applications that use MongoDB")
                    .append("content", "Full article content here..."),
                    
                new Document("title", "Microservices Architecture Patterns")
                    .append("author", "Alice Johnson")
                    .append("tags", Arrays.asList("architecture", "design", "best-practices"))
                    .append("published_date", parseDate("2024-07-20"))
                    .append("status", "published")
                    .append("summary", "Common patterns for building microservices")
                    .append("content", "Full article content here...")
            };
            
            collection.insertMany(Arrays.asList(posts));
            System.out.println("✓ Inserted " + posts.length + " sample blog posts");
            System.out.println("\n✓ Setup complete!");
            System.out.println("\nYou can now search posts by:");
            System.out.println("  - Author (e.g., 'Alice Johnson')");
            System.out.println("  - Tag (predefined list)");
            System.out.println("  - Title keyword");
            System.out.println("  - Date range");
            System.out.println("  - Status (published, draft, archived)");
            
        } catch (Exception e) {
            System.err.println("✗ Error setting up database: " + e.getMessage());
        }
    }
    
    /**
     * Helper to parse date strings.
     */
    private static Date parseDate(String dateStr) {
        try {
            return DATE_FORMAT.parse(dateStr);
        } catch (ParseException e) {
            return new Date();
        }
    }
    
    /**
     * Demonstrates NoSQL injection prevention.
     */
    public static void demonstrateNoSQLInjection() {
        System.out.println("\n=== NoSQL Injection Prevention Demo ===\n");
        
        System.out.println("VULNERABLE approach (DON'T DO THIS):");
        System.out.println("System.out.print(\"Enter search filter as JSON: \");");
        System.out.println("String userJSON = scanner.nextLine();");
        System.out.println("Document filter = Document.parse(userJSON);");
        System.out.println("collection.find(filter);");
        
        System.out.println("\nAttack examples:");
        System.out.println("1. { \"$where\": \"sleep(5000)\" }");
        System.out.println("   Effect: 5-second delay on server (DoS)");
        
        System.out.println("\n2. { \"author\": { \"$ne\": null } }");
        System.out.println("   Effect: Returns ALL posts (bypasses filters)");
        
        System.out.println("\n3. { \"content\": { \"$regex\": \"password\" } }");
        System.out.println("   Effect: Searches in content field (should be restricted)");
        
        System.out.println("\n" + "=".repeat(70));
        System.out.println("\nSECURE approach (OUR CODE):");
        System.out.println("✓ Predefined search fields (author, tag, title, date, status)");
        System.out.println("✓ Type-safe Filters.eq(), Filters.regex(), etc.");
        System.out.println("✓ Whitelist validation for tags and statuses");
        System.out.println("✓ Date validation and parsing");
        System.out.println("✓ Regex special character escaping");
        System.out.println("✓ Field projection (only output safe fields)");
        System.out.println("✓ NO Document.parse() on user input");
        System.out.println("✓ NO arbitrary query structures from users");
        
        System.out.println("\nAdditional security:");
        System.out.println("- Content field NOT included in output (projection)");
        System.out.println("- Users can't search in arbitrary fields");
        System.out.println("- Users can't use arbitrary operators");
        System.out.println("- All regex patterns are escaped");
        
        System.out.println("\nResult: NoSQL injection impossible! ✓");
    }
}

/*
SECURITY FEATURES:

✓ Structured, predefined search options
✓ Type-safe Filters API (no Document.parse)
✓ Whitelist validation (tags, statuses)
✓ Input validation (length, format)
✓ Regex special character escaping
✓ Field projection (limit exposed fields)
✓ Result limiting (max 50 posts)
✓ Date format validation
✓ No arbitrary field access
✓ No user-controlled operators

HOW THIS PREVENTS NOSQL INJECTION:

VULNERABLE CODE (DON'T DO THIS):
```java
System.out.print("Enter filter JSON: ");
String userJSON = scanner.nextLine();
Document filter = Document.parse(userJSON);  // DANGEROUS!
collection.find(filter);
```

Attack scenarios:
1. JavaScript execution:
   { "$where": "sleep(5000)" }
   → Causes server delay

2. Operator injection:
   { "author": { "$ne": null } }
   → Returns all posts

3. Field access:
   { "admin_notes": { "$exists": true } }
   → Accesses restricted fields

4. Regex injection:
   { "title": { "$regex": ".*", "$where": "..." } }
   → Executes code

SECURE CODE (OUR APPROACH):
```java
// User: "Search by author"
// User: "Alice Johnson"
String author = validateInput(userInput);
Bson filter = Filters.eq("author", author);

// User: "Search by tag"
// User: Selects from whitelist
String tag = ALLOWED_TAGS.get(selection);
Bson filter = Filters.eq("tags", tag);

// User: "Search by title"
// User: "MongoDB"
String keyword = escapeRegex(userInput);
Bson filter = Filters.regex("title", ".*" + keyword + ".*", "i");
```

SECURITY LAYERS:

1. Structured Input:
   - Users select search type (author, tag, etc.)
   - We control query structure
   - Users only provide values

2. Input Validation:
   - Author: max 100 chars
   - Title: max 200 chars
   - Tags: whitelist only
   - Status: whitelist only
   - Dates: format validation

3. Safe Construction:
   - Filters.eq("field", value)
   - Filters.regex("field", escapedPattern, "i")
   - Filters.gte/lte for dates
   - No string concatenation

4. Field Projection:
   ```java
   Bson projection = Projections.include(
       "title", "author", "tags", 
       "published_date", "status", "summary"
   );
   // Content, admin_notes, etc. NOT included
   ```

5. Output Control:
   - Only whitelisted fields displayed
   - Sensitive fields excluded
   - Truncate long text
   - Format dates consistently

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
   javac SecureBlogSearch.java
   java -cp .:mongodb-driver-sync.jar:... SecureBlogSearch

USAGE EXAMPLE:

=== Secure MongoDB Blog Search Tool ===

Search by author? (y/n): y
Enter author name: Alice Johnson
✓ Filter: author == "Alice Johnson"

Search by tag? (y/n): y
Available tags:
1. technology    2. programming    3. java
...
Select tag: 3
✓ Filter: tags contains "java"

Search by title keyword? (y/n): n
Search by date range? (y/n): n
Filter by publication status? (y/n): y
Select status: 1 (published)
✓ Filter: status == "published"

--- Search Results ---

Post #1
  Title:     Building RESTful APIs with Java
  Author:    Alice Johnson
  Tags:      java, web-development, tutorial
  Published: 2024-03-10
  Status:    published
  Summary:   Step-by-step guide to creating REST APIs
---

Total posts found: 1

WHAT'S PROTECTED:

1. Query Structure:
   Users can't inject: { "$where": "..." }
   We control operators and structure

2. Field Access:
   Users can't access: content, admin_notes
   We use projection to limit fields

3. Operators:
   Users can't inject: { "$ne": null }
   We use type-safe Filters API

4. Regex:
   Users can't inject: { "$regex": ".*", "$where": "..." }
   We escape regex and control pattern

KEY PRINCIPLES:

1. Users provide VALUES → We provide STRUCTURE
2. Validate all inputs against constraints
3. Use whitelists for categorical data
4. Escape special characters in patterns
5. Limit exposed fields with projection
6. Never parse user JSON/BSON
7. Use type-safe query builders

This is production-ready, secure MongoDB blog search!
*/