import sys
import json

# Check for pymongo installation
try:
    import pymongo
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except ImportError:
    print("Error: 'pymongo' library is missing. Install it via: pip install pymongo")
    sys.exit(1)

def get_db_collection():
    """
    Connects to the MongoDB server and returns the 'users' collection.
    Adjust the connection string for your specific setup.
    """
    # Standard local connection string
    # For MongoDB Atlas (Cloud), replace with: "mongodb+srv://<user>:<pass>@cluster.mongodb.net/"
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    
    try:
        # Trigger a server check to fail fast if not connected
        client.admin.command('ping')
        
        db = client["user_database"]
        return db["users"]
    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("Error: Could not connect to MongoDB. Is the server running on localhost:27017?")
        sys.exit(1)

def setup_dummy_data(collection):
    """
    Seeds the database with sample data if it's empty.
    """
    if collection.count_documents({}) == 0:
        print("Seeding database with sample users...")
        sample_users = [
            {"name": "Alice Smith", "age": 28, "country": "USA", "role": "admin"},
            {"name": "Bob Jones", "age": 35, "country": "UK", "role": "user"},
            {"name": "Charlie Brown", "age": 22, "country": "Canada", "role": "user"},
            {"name": "David Lee", "age": 40, "country": "USA", "role": "moderator"},
            {"name": "Eva Green", "age": 29, "country": "Germany", "role": "user"},
            {"name": "Frank White", "age": 31, "country": "USA", "role": "user"}
        ]
        collection.insert_many(sample_users)
        print("Seed complete.")

def filter_users():
    print("--- MongoDB User Filter ---")
    
    collection = get_db_collection()
    setup_dummy_data(collection)

    print("\nQuery Format: Enter a valid JSON object.")
    print("Examples:")
    print("  - Exact match:     {\"country\": \"USA\"}")
    print("  - Greater than:    {\"age\": {\"$gt\": 30}}")
    print("  - Multiple fields: {\"country\": \"USA\", \"role\": \"user\"}")
    
    user_input = input("\nEnter filter condition: ").strip()

    if not user_input:
        print("No condition entered. Exiting.")
        return

    try:
        # 1. Parse the input string into a Python dictionary (JSON)
        query_filter = json.loads(user_input)
        
        # 2. Execute the query
        # In MongoDB, the 'find' method accepts a dictionary as the filter.
        results = list(collection.find(query_filter, {"_id": 0})) # Exclude _id for cleaner output
        
        print(f"\nFound {len(results)} matching user(s):")
        print("-" * 50)
        
        if results:
            for user in results:
                # Pretty print the user record
                print(json.dumps(user, indent=2))
                print("-" * 20)
        else:
            print("No users found matching that condition.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON format. Make sure to use double quotes around keys and strings.")
        print("Correct Example: {\"age\": 25}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    filter_users()