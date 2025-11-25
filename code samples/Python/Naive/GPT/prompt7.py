#!/usr/bin/env python3
import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def main():
    # Adjust this URI and database/collection names as needed
    mongo_uri = "mongodb://localhost:27017"
    db_name = "blog"
    collection_name = "posts"

    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        posts = db[collection_name]
    except PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    print("Search blog posts using a MongoDB filter.")
    print('Enter a filter as a JSON object, for example:')
    print('  {"author": "Alice"}')
    print('  {"tags": "python"}')
    print('  {"tags": {"$in": ["python", "mongodb"]}}')
    print("Leave empty for no filter (match all posts).")
    print()

    filter_str = input("Filter JSON: ").strip()

    if not filter_str:
        query_filter = {}
    else:
        try:
            query_filter = json.loads(filter_str)
            if not isinstance(query_filter, dict):
                print("The filter must be a JSON object (e.g. {\"author\": \"Alice\"}).")
                return
        except json.JSONDecodeError as e:
            print(f"Invalid JSON filter: {e}")
            return

    try:
        cursor = posts.find(query_filter, {"title": 1, "_id": 0})
        found_any = False
        print("\nMatching post titles:")
        print("----------------------")
        for doc in cursor:
            found_any = True
            title = doc.get("title", "<no title>")
            print(f"- {title}")

        if not found_any:
            print("No posts matched the given filter.")
    except PyMongoError as e:
        print(f"Error running query: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()