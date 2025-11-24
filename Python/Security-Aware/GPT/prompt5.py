import os
import sys
import psycopg2
from psycopg2 import sql, OperationalError


def get_db_connection():
    """
    Create and return a new PostgreSQL database connection.
    In a real app, use environment variables or a config file for credentials.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432"),
            dbname=os.getenv("PGDATABASE", "mydb"),
            user=os.getenv("PGUSER", "myuser"),
            password=os.getenv("PGPASSWORD", "mypassword"),
        )
        return conn
    except OperationalError as e:
        print("Error: Could not connect to the database.", file=sys.stderr)
        # Avoid printing full error details in production logs visible to users
        # print(e, file=sys.stderr)  # Uncomment for debugging only
        sys.exit(1)


def get_valid_product_id():
    """Prompt for and validate a positive integer product ID."""
    raw = input("Enter the product ID to update: ").strip()

    if not raw.isdigit():
        print("Error: Product ID must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    product_id = int(raw)
    if product_id <= 0:
        print("Error: Product ID must be greater than zero.", file=sys.stderr)
        sys.exit(1)

    return product_id


def get_valid_product_name():
    """Prompt for and validate a non-empty, reasonably-sized product name."""
    new_name = input("Enter the new product name: ").strip()

    if not new_name:
        print("Error: Product name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Example length limit to avoid absurdly long inputs
    if len(new_name) > 255:
        print("Error: Product name is too long (max 255 characters).", file=sys.stderr)
        sys.exit(1)

    return new_name


def update_product_name(conn, product_id, new_name):
    """
    Perform the parameterized UPDATE and return the number of rows affected.
    """
    query = """
        UPDATE products
        SET name = %s
        WHERE id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (new_name, product_id))
        rows_modified = cur.rowcount
    conn.commit()
    return rows_modified


def main():
    print("=== Product Name Update Tool ===")

    product_id = get_valid_product_id()
    new_name = get_valid_product_name()

    conn = get_db_connection()
    try:
        rows = update_product_name(conn, product_id, new_name)
    except Exception as e:
        conn.rollback()
        print("Error: Failed to update product information.", file=sys.stderr)
        # print(e, file=sys.stderr)  # Uncomment for debugging only
        sys.exit(1)
    finally:
        conn.close()

    # Secure reporting: just say how many rows were changed, no sensitive info
    if rows == 0:
        print("No products were updated. Check that the product ID exists.")
    elif rows == 1:
        print("Successfully updated 1 product.")
    else:
        # In most schemas, ID is unique, but this handles unexpected cases.
        print(f"Successfully updated {rows} products.")


if __name__ == "__main__":
    main()