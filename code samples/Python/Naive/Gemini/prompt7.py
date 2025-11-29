import sys
import json
import datetime

# Check for pymongo installation
try:
    import pymongo
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except ImportError:
    print("Error: 'pymongo' library is missing. Install it via: pip install pymongo")
    sys.exit(1)

def get_db_collection():
    """
    Connects to the MongoDB server and returns the 'posts' collection.
    """
    # Standard local connection string
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    
    try:
        # Fail fast if not connected
        client.admin.command('ping')
        db = client["blog_database"]
        return db["posts"]
    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("Error: Could not connect to MongoDB. Is the server running on localhost:27017?")
        sys.exit(1)

def setup_dummy_data(collection):
    """
    Seeds the database with sample blog posts if it's empty.
    """
    if collection.count_documents({}) == 0:
        print("Seeding database with sample blog posts...")
        sample_posts = [
            {
                "title": "Getting Started with Python",
                "author": "Alice",
                "tags": ["python", "coding", "tutorial"],
                "views": 150,
                "date": datetime.datetime(2023, 1, 15)
            },
            {
                "title": "Deep Dive into MongoDB",
                "author": "Bob",
                "tags": ["database", "nosql", "mongodb"],
                "views": 320,
                "date": datetime.datetime(2023, 2, 10)
            },
            {
                "title": "Advanced Python Tips",
                "author": "Alice",
                "tags": ["python", "advanced"],
                "views": 500,
                "date": datetime.datetime(2023, 3, 5)
            },
            {
                "title": "Why SQL is still relevant",
                "author": "Charlie",
                "tags": ["database", "sql", "opinion"],
                "views": 120,
                "date": datetime.datetime(2023, 3, 20)
            },
            {
                "title": "Web Development Trends 2024",
                "author": "Bob",
                "tags": ["web", "javascript", "react"],
                "views": 1000,
                "date": datetime.datetime(2023, 4, 1)
            }
        ]
        collection.insert_many(sample_posts)
        print("Seed complete.")

def search_blog_posts():
    print("--- Blog Post Search Tool ---")
    
    collection = get_db_collection()
    setup_dummy_data(collection)

    print("\nSearch by entering a JSON filter.")
    print("Examples:")
    print("  - By Author:       {\"author\": \"Alice\"}")
    print("  - By Tag:          {\"tags\": \"python\"}")
    print("  - Popular posts:   {\"views\": {\"$gt\": 200}}")
    print("  - Complex:         {\"author\": \"Bob\", \"tags\": \"database\"}")
    
    user_input = input("\nEnter filter expression: ").strip()

    if not user_input:
        print("No filter entered. Exiting.")
        return

    try:
        # 1. Parse user input as JSON
        query_filter = json.loads(user_input)
        
        # 2. Execute query
        # We project only the fields we want to display (0 hides _id, 1 shows the field)
        cursor = collection.find(query_filter, {"_id": 0, "title": 1, "author": 1, "tags": 1})
        results = list(cursor)
        
        print(f"\nFound {len(results)} matching post(s):")
        print("-" * 50)
        
        if results:
            for post in results:
                print(f"Title:  {post.get('title')}")
                print(f"Author: {post.get('author')}")
                # Join tags list into a string for display
                tags_display = ", ".join(post.get('tags', []))
                print(f"Tags:   {tags_display}")
                print("-" * 50)
        else:
            print("No posts found matching that filter.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON format. Ensure keys are in double quotes.")
        print("Correct: {\"tags\": \"python\"}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    search_blog_posts()