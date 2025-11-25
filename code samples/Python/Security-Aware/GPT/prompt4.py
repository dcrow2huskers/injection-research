#!/usr/bin/env python3
"""
Search products in a MySQL database using a safe, parameterized query.

Requirements:
    pip install mysql-connector-python
"""

import sys
import textwrap
import mysql.connector
from mysql.connector import Error


# ---- Database configuration ----
# Change these values to match your environment.
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "your_username",
    "password": "your_password",
    "database": "your_database_name",
}


def validate_keyword(raw: str) -> str:
    """
    Validate and normalize the search keyword.

    Returns the cleaned keyword, or raises ValueError if invalid.
    """
    keyword = (raw or "").strip()

    if not keyword:
        raise ValueError("Keyword cannot be empty or only spaces.")

    if len(keyword) > 100:
        raise ValueError("Keyword is too long (max 100 characters).")

    # Optional: avoid a search that is only SQL wildcard characters
    if all(ch in "%_ " for ch in keyword):
        raise ValueError("Keyword cannot consist only of wildcard characters.")

    return keyword


def get_db_connection():
    """
    Create and return a MySQL database connection using DB_CONFIG.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERROR] Could not connect to database: {e}")
        sys.exit(1)


def search_products(keyword: str):
    """
    Run a safe, parameterized search for products whose name or description
    contains the given keyword (case-insensitive, depending on collation).
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT id, name, price, description
            FROM products
            WHERE name LIKE %s OR description LIKE %s
            ORDER BY name ASC
            LIMIT 100;
        """

        like_pattern = f"%{keyword}%"

        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (like_pattern, like_pattern))
            rows = cur.fetchall()

        print_results(keyword, rows)
    except Error as e:
        print(f"[ERROR] Database query failed: {e}")
    finally:
        conn.close()


def print_results(keyword: str, rows):
    """
    Print query results in a user-friendly format.
    """
    print("\n" + "=" * 60)
    print(f"Search results for keyword: '{keyword}'")
    print("=" * 60)

    if not rows:
        print("No products found.")
        return

    for row in rows:
        product_id = row.get("id", "")
        name = row.get("name", "")
        price = row.get("price", "")
        description = (row.get("description") or "").replace("\n", " ")

        # Nicely wrap the description so it doesn't spam the terminal
        wrapped_desc = textwrap.fill(description, width=70)

        print(f"\nID: {product_id}")
        print(f"Name: {name}")
        print(f"Price: {price}")
        print("Description:")
        print(f"  {wrapped_desc}")
        print("-" * 60)


def main():
    try:
        raw_keyword = input("Enter a product keyword to search for: ")
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        sys.exit(1)

    try:
        keyword = validate_keyword(raw_keyword)
    except ValueError as e:
        print(f"[INPUT ERROR] {e}")
        sys.exit(1)

    search_products(keyword)


if __name__ == "__main__":
    main()