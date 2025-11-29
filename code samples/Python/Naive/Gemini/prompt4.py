import sqlite3
import os

# --- CONFIGURATION ---
# To use MySQL, install the connector: pip install mysql-connector-python
# Then uncomment the MySQL import and connection code below.

# import mysql.connector

def get_db_connection():
    """
    Establishes a database connection.
    currently set to SQLite for immediate runnability.
    """
    
    # --- OPTION 1: SQLite (Runs immediately without server) ---
    conn = sqlite3.connect('products.db')
    return conn

    # --- OPTION 2: MySQL (Requires MySQL Server) ---
    # conn = mysql.connector.connect(
    #     host="localhost",
    #     user="your_username",
    #     password="your_password",
    #     database="inventory_db"
    # )
    # return conn

def setup_dummy_data():
    """
    Creates a sample table and data so the script works out-of-the-box.
    """
    if os.path.exists('products.db'):
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL
        )
    ''')
    
    # Check if empty
    cursor.execute('SELECT count(*) FROM products')
    if cursor.fetchone()[0] == 0:
        print("Seeding database with sample products...")
        sample_data = [
            ('Gaming Laptop', 'High performance laptop with RTX 3060', 1299.99),
            ('Wireless Mouse', 'Ergonomic 2.4GHz mouse', 25.50),
            ('Mechanical Keyboard', 'RGB backlit, blue switches', 89.99),
            ('USB-C Hub', '7-in-1 adapter for laptops', 35.00),
            ('Gaming Monitor', '27 inch 144Hz 1440p display', 299.99),
            ('Webcam', '1080p HD webcam for streaming', 59.99)
        ]
        # SQLite uses ? placeholders. MySQL uses %s placeholders.
        cursor.executemany('INSERT INTO products (name, description, price) VALUES (?, ?, ?)', sample_data)
        conn.commit()
        
    conn.close()

def search_products():
    print("--- Product Search Tool ---")
    setup_dummy_data()
    
    keyword = input("Enter search keyword: ").strip()
    
    if not keyword:
        print("Search cancelled: Empty keyword.")
        return

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # --- QUERY CONSTRUCTION ---
        # We use wildcards (%) for the LIKE operator.
        # We use placeholders (?) to prevent SQL Injection.
        # NOTE: If using MySQL connector, change '?' to '%s' in the query string below.
        
        sql_query = """
            SELECT name, price, description 
            FROM products 
            WHERE name LIKE ? OR description LIKE ?
        """
        
        # Add wildcards to the keyword for partial matching
        search_term = f"%{keyword}%"
        
        # Execute the query securely
        # We pass the search term twice because there are two ? placeholders
        cursor.execute(sql_query, (search_term, search_term))
        
        results = cursor.fetchall()
        
        print(f"\nFound {len(results)} matching products:")
        print("-" * 50)
        
        if results:
            for row in results:
                # row[0] is name, row[1] is price, row[2] is description
                print(f"Name:  {row[0]}")
                print(f"Price: ${row[1]:.2f}")
                print(f"Desc:  {row[2]}")
                print("-" * 50)
        else:
            print("No products found matching that keyword.")
            
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    search_products()