import psycopg2
from psycopg2 import Error
import getpass
import sys

# Database Configuration
# In production, load these from environment variables or a secure vault
DB_CONFIG = {
    'host': 'localhost',
    'database': 'inventory_db',
    'user': 'postgres',
    'port': '5432'
}

def get_db_connection(password):
    """Establishes a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=password,
            port=DB_CONFIG['port']
        )
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def update_product_name(connection, product_id, new_name):
    """
    Updates a product's name using a secure parameterized query.
    """
    cursor = connection.cursor()
    
    # SQL query with placeholders
    # psycopg2 uses %s for placeholders, similar to the MySQL connector
    sql_update = """
        UPDATE products 
        SET name = %s 
        WHERE id = %s
    """
    
    try:
        # Execute the update securely
        # The library handles escaping, preventing SQL injection
        cursor.execute(sql_update, (new_name, product_id))
        
        # In PostgreSQL, you must commit changes for them to take effect
        connection.commit()
        
        rows_affected = cursor.rowcount
        
        if rows_affected > 0:
            print(f"\n[SUCCESS] Updated {rows_affected} row(s).")
            print(f"Product ID {product_id} is now named '{new_name}'.")
        else:
            print(f"\n[INFO] No rows updated. Product ID {product_id} might not exist.")

    except Error as e:
        print(f"Error executing update: {e}")
        # Rollback in case of error to keep transaction state clean
        connection.rollback()
    finally:
        if cursor:
            cursor.close()

def validate_id(id_input):
    """Ensures ID is a valid integer."""
    try:
        val = int(id_input)
        if val < 0:
            print("ID must be positive.")
            return None
        return val
    except ValueError:
        print("Invalid ID format. Please enter a number.")
        return None

def main():
    print("--- Secure PostgreSQL Product Updater ---")
    
    # 1. Connect to Database
    print(f"Connecting to {DB_CONFIG['host']} as {DB_CONFIG['user']}...")
    db_pass = getpass.getpass("Enter Database Password: ")
    
    conn = get_db_connection(db_pass)
    if not conn:
        sys.exit(1)

    print("\nConnection successful.")

    # 2. Main Update Loop
    try:
        while True:
            print("\n--- Update Product ---")
            id_input = input("Enter Product ID (or 'q' to quit): ").strip()
            
            if id_input.lower() == 'q':
                break
            
            # Validate ID
            product_id = validate_id(id_input)
            if product_id is None:
                continue
                
            # Get and Validate New Name
            new_name = input(f"Enter new name for Product ID {product_id}: ").strip()
            if not new_name:
                print("Error: Product name cannot be empty.")
                continue
            
            # Confirm Action
            confirm = input(f"Are you sure you want to rename ID {product_id} to '{new_name}'? (y/n): ")
            if confirm.lower() == 'y':
                update_product_name(conn, product_id, new_name)
            else:
                print("Update cancelled.")

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()