#!/usr/bin/env python3
"""
Secure MongoDB blog search CLI tool.

- Connects to a MongoDB "blog" database.
- Lets the user search posts by predefined fields:
  * author (exact match)
  * tag (exact match, in tags list)
  * date range (on published_at)
- Validates input and constructs the query dict programmatically.
- Does NOT evaluate or interpret raw user-provided query structures.
- Outputs only intended fields from the matching posts.
"""

import sys
from datetime import datetime
from typing import Dict, Any, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ---- Configuration ----
MONGO_URI = "mongodb://localhost:27017"  # Adjust as needed
DB_NAME = "blog"
COLLECTION_NAME = "posts"

# Fields we will ever return to the user
OUTPUT_PROJECTION = {
    "_id": 0,          # explicitly exclude MongoDB's internal _id
    "title": 1,
    "author": 1,
    "tags": 1,
    "published_at": 1,
}


def connect_to_mongo(uri: str, db_name: str, collection_name: str):
    """Create a MongoDB client and return the collection object."""
    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]


def prompt_yes_no(message: str) -> bool:
    """Simple yes/no prompt, returns True for yes, False for no."""
    while True:
        answer = input(f"{message} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def prompt_non_empty(prompt_text: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def prompt_date(prompt_text: str) -> Optional[datetime]:
    """
    Prompt for a date in YYYY-MM-DD format.
    Returns a datetime.date (midnight UTC) or None if user leaves empty.
    """
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return None
        try:
            # Interpret as date at midnight
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD, or leave blank.")


def build_query() -> Dict[str, Any]:
    """
    Interactively build a MongoDB query with validated, structured input.
    Only allows searching on whitelisted fields.
    """
    query: Dict[str, Any] = {}

    print("=== Blog Post Search ===")
    print("You can search by one or more of the following fields:")
    print("  1) author (exact match)")
    print("  2) tag (exact match; post must contain this tag)")
    print("  3) date range (on published_at, YYYY-MM-DD)")

    # Author filter
    if prompt_yes_no("Filter by author?"):
        author = prompt_non_empty("Enter author name: ")
        # Safe, fixed field name; user controls only the value
        query["author"] = author

    # Tag filter
    if prompt_yes_no("Filter by tag?"):
        tag = prompt_non_empty("Enter tag: ")
        # Assuming posts have a 'tags' array
        query["tags"] = tag

    # Date range filter
    if prompt_yes_no("Filter by published date range?"):
        print("Enter start and/or end date in YYYY-MM-DD format.")
        print("Leave blank to omit start/end boundary.")

        start_date = prompt_date("Start date (>=): ")
        end_date = prompt_date("End date (<=): ")

        if start_date or end_date:
            date_filter: Dict[str, Any] = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                # To include full end date, we can set time to end-of-day if desired.
                # For simplicity, assume datetime is inclusive as-is.
                date_filter["$lte"] = end_date

            # Again, fixed field name; only operator values vary
            query["published_at"] = date_filter

    if not query:
        print("\nNo filters selected. This will return all posts.")
        if not prompt_yes_no("Continue with no filters?"):
            print("Aborting search.")
            sys.exit(0)

    return query


def print_results(cursor):
    """Print matching posts, showing only intended fields."""
    count = 0
    print("\n=== Search Results ===\n")
    for post in cursor:
        count += 1
        title = post.get("title", "<no title>")
        author = post.get("author", "<unknown author>")
        tags = post.get("tags", [])
        published_at = post.get("published_at")

        print(f"Title:  {title}")
        print(f"Author: {author}")

        if isinstance(tags, list):
            print(f"Tags:   {', '.join(str(t) for t in tags) if tags else '(none)'}")
        else:
            print("Tags:   (malformed or missing)")

        if isinstance(published_at, datetime):
            print(f"Date:   {published_at.strftime('%Y-%m-%d')}")
        else:
            print("Date:   (unknown)")

        print("-" * 40)

    if count == 0:
        print("No posts matched your search criteria.")
    else:
        print(f"\nTotal posts found: {count}")


def main():
    try:
        collection = connect_to_mongo(MONGO_URI, DB_NAME, COLLECTION_NAME)
    except PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

    query = build_query()

    try:
        cursor = collection.find(query, projection=OUTPUT_PROJECTION)
        print_results(cursor)
    except PyMongoError as e:
        print(f"Error querying MongoDB: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()