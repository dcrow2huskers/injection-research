import sys
import os

# --- CONFIGURATION ---
# Set this to True to use a real PostgreSQL database.
# Set this to False to use a local SQLite file for testing immediately.
USE_POSTGRES = False

if USE_POSTGRES:
    try:
        import psycopg2
    except ImportError:
        print("Error: 'psycopg2' library is missing. Install it via: pip install psycopg2")
        sys.exit(1)
else:
    import sqlite3

def get_db_connection():
    """
    Connects to the database based on the USE_POSTGRES flag.
    """
    if USE_POSTGRES:
        # Update these parameters for your actual PostgreSQL server
        return psycopg2.connect(
            host="localhost",
            database="inventory_db",
            user="postgres",
            password="your_password"
        )
    else:
        # Connects to the local file created by the previous script
        return sqlite3.connect('products.db')

def setup_demo_data():
    """Ensures there is data to update if running in demo mode."""
    if not os.path.exists('products.db') and not USE_POSTGRES:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL)')
        cursor.execute("INSERT INTO products (name, price) VALUES ('Generic Laptop', 500.0)")
        conn.commit()
        conn.close()
        print("(Created demo database 'products.db' with sample data)")

def update_product_name():
    print("--- Update Product Name ---")
    
    # 1. Setup/Check
    if not USE_POSTGRES:
        setup_demo_data()

    # 2. Get User Input
    try:
        product_id = int(input("Enter Product ID to update: "))
    except ValueError:
        print("Error: Product ID must be a number.")
        return

    new_name = input("Enter new product name: ").strip()
    if not new_name:
        print("Operation cancelled: Name cannot be empty.")
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 3. Construct the SQL Query
        # PostgreSQL uses '%s' for placeholders. SQLite uses '?'.
        # We detect the mode to use the correct syntax.
        placeholder = "%s" if USE_POSTGRES else "?"
        
        sql_query = f"UPDATE products SET name = {placeholder} WHERE id = {placeholder}"
        
        # 4. Execute the Update
        # Passing variables separately prevents SQL Injection
        cursor.execute(sql_query, (new_name, product_id))
        
        # 5. Commit the transaction (CRITICAL for updates)
        # Without this, the change will be lost when the script ends.
        conn.commit()
        
        # 6. Report result
        # cursor.rowcount tells us how many rows matched the criteria
        rows_updated = cursor.rowcount
        
        print("-" * 30)
        if rows_updated > 0:
            print(f"Success! Updated {rows_updated} row(s).")
        else:
            print("No rows updated. That Product ID might not exist.")

    except Exception as e:
        print(f"Database Error: {e}")
        if conn:
            conn.rollback() # Undo changes if an error occurs
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_product_name()