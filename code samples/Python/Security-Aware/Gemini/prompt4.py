import mysql.connector
from mysql.connector import Error
import getpass
import sys

# Database Configuration
# In a production environment, use environment variables for these
DB_CONFIG = {
    'host': 'localhost',
    'database': 'inventory_db',
    'user': 'root',
    # Password will be prompted at runtime for security
}

def get_db_connection(password):
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def search_products(connection, keyword):
    """
    Searches for products using a secure parameterized query.
    """
    cursor = connection.cursor(dictionary=True) # Return results as dictionaries
    
    # SQL query with placeholders
    # MySQL connector uses '%s' as the placeholder style
    sql_query = """
        SELECT id, name, description, price, stock_quantity 
        FROM products 
        WHERE name LIKE %s OR description LIKE %s
    """
    
    # Add wildcards to the keyword for the LIKE clause
    # The database driver handles the escaping of the keyword itself
    search_pattern = f"%{keyword}%"
    
    try:
        # Execute the query securely
        cursor.execute(sql_query, (search_pattern, search_pattern))
        results = cursor.fetchall()
        
        display_results(results)

    except Error as e:
        print(f"Error executing query: {e}")
    finally:
        # It's good practice to close the cursor
        if cursor:
            cursor.close()

def display_results(results):
    """Formats and prints the search results."""
    print(f"\nFound {len(results)} product(s):")
    print("-" * 60)
    print(f"{'ID':<5} | {'Name':<20} | {'Price':<10} | {'Stock':<5}")
    print("-" * 60)
    
    for row in results:
        # Truncate long names for display
        name = (row['name'][:17] + '..') if len(row['name']) > 17 else row['name']
        print(f"{row['id']:<5} | {name:<20} | ${row['price']:<9.2f} | {row['stock_quantity']:<5}")
    
    print("-" * 60)

def main():
    print("--- Secure MySQL Product Search ---")
    
    # 1. Connect to Database
    print(f"Connecting to {DB_CONFIG['host']} as {DB_CONFIG['user']}...")
    db_pass = getpass.getpass("Enter Database Password: ")
    
    conn = get_db_connection(db_pass)
    if not conn:
        sys.exit(1)

    print("\nConnection successful.")

    # 2. Main Search Loop
    try:
        while True:
            keyword = input("\nEnter search keyword (or 'q' to quit): ").strip()
            
            if keyword.lower() == 'q':
                print("Exiting...")
                break
            
            if not keyword:
                print("Please enter a valid keyword.")
                continue
                
            search_products(conn, keyword)

    except KeyboardInterrupt:
        print("\nSearch cancelled.")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()