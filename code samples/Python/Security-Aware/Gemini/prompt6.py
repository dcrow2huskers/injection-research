import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import sys

# Database Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "user_directory"
COLLECTION_NAME = "users"

def get_db_collection():
    """Establishes a connection to the MongoDB collection."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Trigger a simple command to verify connection
        client.admin.command('ping')
        
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except ConnectionFailure:
        print("Error: Could not connect to MongoDB server.")
        return None

def get_integer_input(prompt):
    """Safely gets an integer input from the user."""
    while True:
        value = input(prompt).strip()
        if not value:
            return None # Return None if user skips
        try:
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def build_secure_query():
    """
    Constructs a MongoDB query dictionary based on user inputs.
    
    Security Note:
    This function avoids NoSQL injection by strictly typing inputs (integers)
    and building the query dictionary programmatically rather than 
    concatenating strings or using the insecure '$where' operator.
    """
    query = {}
    print("\n--- Define Filter Criteria (Press Enter to skip a filter) ---")

    # 1. Country Filter (Exact Match)
    country = input("Filter by Country (e.g., USA, Japan): ").strip()
    if country:
        # Direct assignment is safe; MongoDB drivers treat value as a literal
        query['country'] = country

    # 2. Age Range Filter
    min_age = get_integer_input("Minimum Age: ")
    max_age = get_integer_input("Maximum Age: ")

    if min_age is not None or max_age is not None:
        query['age'] = {}
        if min_age is not None:
            query['age']['$gte'] = min_age
        if max_age is not None:
            query['age']['$lte'] = max_age

    # 3. Role Filter (Whitelist validation)
    role = input("Filter by Role (admin/editor/viewer): ").strip().lower()
    if role:
        allowed_roles = {'admin', 'editor', 'viewer'}
        if role in allowed_roles:
            query['role'] = role
        else:
            print(f"Warning: '{role}' is not a valid role. Ignoring role filter.")

    return query

def display_users(collection, query):
    """Executes the query and displays results."""
    print(f"\nExecuting Query: {query}")
    
    try:
        # Find returns a cursor, which we iterate over
        cursor = collection.find(query, {'_id': 0, 'password': 0}) # Exclude _id and password
        
        count = collection.count_documents(query)
        print(f"Found {count} matching user(s):\n")
        
        if count > 0:
            print(f"{'Name':<20} | {'Age':<5} | {'Country':<15} | {'Role':<10}")
            print("-" * 60)
            for user in cursor:
                name = user.get('name', 'N/A')
                age = user.get('age', 'N/A')
                country = user.get('country', 'N/A')
                role = user.get('role', 'N/A')
                print(f"{name:<20} | {age:<5} | {country:<15} | {role:<10}")
        else:
            print("No records found matching criteria.")
            
    except OperationFailure as e:
        print(f"Database error: {e}")

def main():
    print("--- MongoDB User Filter Tool ---")
    
    collection = get_db_collection()
    if not collection:
        sys.exit(1)

    while True:
        query = build_secure_query()
        display_users(collection, query)

        again = input("\nSearch again? (y/n): ").strip().lower()
        if again != 'y':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()