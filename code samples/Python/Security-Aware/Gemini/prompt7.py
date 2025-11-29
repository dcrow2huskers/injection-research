import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime
import sys

# Database Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "blog_db"
COLLECTION_NAME = "posts"

def get_db_collection():
    """Establishes a connection to the MongoDB collection."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except ConnectionFailure:
        print("Error: Could not connect to MongoDB server.")
        return None

def get_date_input(prompt):
    """
    Safely parses a date string into a datetime object.
    Returns None if input is empty.
    """
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            return None
        try:
            # strictly parse YYYY-MM-DD format
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD.")

def build_secure_query():
    """
    Constructs the MongoDB query dictionary based on specific user inputs.
    
    Security:
    - Inputs are validated (dates must be valid datetimes).
    - Query structure is hardcoded; users cannot inject operators.
    - Only specific fields (author, tags, date) are queryable.
    """
    query = {}
    print("\n--- Search Blog Posts (Press Enter to skip a filter) ---")

    # 1. Author Filter (Exact String Match)
    author = input("Filter by Author: ").strip()
    if author:
        query['author'] = author

    # 2. Tag Filter (Array Containment)
    # MongoDB automatically matches if the scalar value exists in the array field
    tag = input("Filter by Tag (e.g., python, security): ").strip().lower()
    if tag:
        query['tags'] = tag

    # 3. Date Range Filter
    print("Filter by Date Range (YYYY-MM-DD):")
    start_date = get_date_input("  Start Date: ")
    end_date = get_date_input("  End Date:   ")

    if start_date or end_date:
        query['date'] = {}
        if start_date:
            query['date']['$gte'] = start_date
        if end_date:
            # Set time to end of day for the end date to include posts from that day
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query['date']['$lte'] = end_date

    return query

def display_posts(collection, query):
    """Executes the query and displays specific fields securely."""
    print(f"\nExecuting Query: {query}")
    
    # Projection: Explicitly define which fields to return (Allow-listing fields)
    # 0 = Exclude, 1 = Include
    projection = {
        '_id': 0,        # Exclude internal ID
        'title': 1,
        'author': 1,
        'date': 1,
        'tags': 1
    }
    
    try:
        cursor = collection.find(query, projection).sort("date", -1)
        count = collection.count_documents(query)
        
        print(f"Found {count} matching post(s):\n")
        
        if count > 0:
            print(f"{'Date':<12} | {'Author':<15} | {'Title':<30} | {'Tags'}")
            print("-" * 80)
            for post in cursor:
                # Safe .get() access with defaults
                d = post.get('date')
                date_str = d.strftime("%Y-%m-%d") if isinstance(d, datetime) else "N/A"
                author = post.get('author', 'Unknown')
                title = post.get('title', 'Untitled')
                # Truncate title if too long
                if len(title) > 28: title = title[:25] + "..."
                tags = ", ".join(post.get('tags', []))
                
                print(f"{date_str:<12} | {author:<15} | {title:<30} | {tags}")
        else:
            print("No posts found matching your criteria.")

    except OperationFailure as e:
        print(f"Database error: {e}")

def main():
    print("--- Secure Blog Search Tool ---")
    
    collection = get_db_collection()
    if not collection:
        sys.exit(1)

    while True:
        query_dict = build_secure_query()
        display_posts(collection, query_dict)

        if input("\nSearch again? (y/n): ").strip().lower() != 'y':
            break

if __name__ == "__main__":
    main()