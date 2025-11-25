#!/usr/bin/env python3
"""
Secure MongoDB user filter script.

- Connects to a MongoDB database.
- Lets the user filter users based on chosen criteria.
- Provides clearly defined filter options (age ranges, country values).
- Validates user input.
- Builds the query document programmatically (no eval/exec or arbitrary expressions).
- Displays matching user records safely.
"""

from typing import Dict, Any, Optional, List
from pymongo import MongoClient


# ---- Configuration ----
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "mydatabase"
COLLECTION_NAME = "users"

# Whitelisted countries the user can choose from
ALLOWED_COUNTRIES = [
    "US", "UK", "CA", "DE", "FR", "IN", "CN", "BR", "AU", "JP"
]

# ---- Input helpers ----

def prompt_int(prompt: str, min_value: Optional[int] = None,
               max_value: Optional[int] = None) -> int:
    """Prompt the user for an integer with optional min/max validation."""
    while True:
        value_str = input(prompt).strip()
        if not value_str:
            print("Input cannot be empty.")
            continue
        try:
            value = int(value_str)
        except ValueError:
            print("Please enter a valid integer.")
            continue

        if min_value is not None and value < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return value


def prompt_choice(prompt: str, choices: List[str]) -> str:
    """Prompt the user to select from a list of string choices."""
    lower_choices = [c.lower() for c in choices]
    while True:
        value = input(prompt).strip()
        if not value:
            print("Input cannot be empty.")
            continue
        if value.lower() in lower_choices:
            # Return the original casing from choices list
            return choices[lower_choices.index(value.lower())]
        print(f"Invalid choice. Please choose one of: {', '.join(choices)}")


def build_filter() -> Dict[str, Any]:
    """
    Interactively build a MongoDB filter document based on user selections.
    Returns a dictionary suitable for use as a MongoDB query.
    """
    query: Dict[str, Any] = {}

    print("Choose filter options:")
    print("  1) Filter by age range")
    print("  2) Filter by country")
    print("  3) Filter by age range AND country")
    print("  4) No filters (show all users)")

    selection = prompt_choice("Enter 1, 2, 3, or 4: ", ["1", "2", "3", "4"])

    if selection in ("1", "3"):
        print("\n-- Age range filter --")
        # Reasonable bounds for age; adjust as needed
        min_age = prompt_int("Minimum age (0–120): ", min_value=0, max_value=120)
        max_age = prompt_int("Maximum age (0–120): ", min_value=0, max_value=120)

        if max_age < min_age:
            print("Maximum age is less than minimum age; swapping them.")
            min_age, max_age = max_age, min_age

        query["age"] = {"$gte": min_age, "$lte": max_age}

    if selection in ("2", "3"):
        print("\n-- Country filter --")
        print("Available countries:")
        for c in ALLOWED_COUNTRIES:
            print(f"  - {c}")
        country = prompt_choice("Enter a country code from the list above: ",
                                ALLOWED_COUNTRIES)
        query["country"] = country

    return query


def display_results(results) -> None:
    """Safely display user records."""
    print("\nMatching user records:")
    count = 0
    for doc in results:
        count += 1
        # Convert ObjectId to string for safe/clean display if present
        doc_id = str(doc.get("_id", "N/A"))
        name = doc.get("name", "N/A")
        age = doc.get("age", "N/A")
        country = doc.get("country", "N/A")
        email = doc.get("email", "N/A")

        print("-" * 40)
        print(f"ID:      {doc_id}")
        print(f"Name:    {name}")
        print(f"Age:     {age}")
        print(f"Country: {country}")
        print(f"Email:   {email}")

    if count == 0:
        print("No matching users found.")
    else:
        print("-" * 40)
        print(f"Total matches: {count}")


def main() -> None:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users = db[COLLECTION_NAME]

    print("Secure MongoDB User Filter")
    print("==========================")

    # Build the query document programmatically
    query = build_filter()
    print("\nRunning query:", query)

    # Perform the query
    cursor = users.find(query)

    # Display the results safely
    display_results(cursor)


if __name__ == "__main__":
    main()