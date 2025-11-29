import psycopg2
from psycopg2 import Error

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        connection = psycopg2.connect(
            host='localhost',
            database='your_database_name',
            user='your_username',
            password='your_password',
            port='5432'
        )
        print("Successfully connected to PostgreSQL database\n")
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_product_info(connection, product_id):
    """Display current product information before updating"""
    try:
        cursor = connection.cursor()
        query = "SELECT id, name FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            print(f"\nCurrent product info:")
            print(f"  ID: {result[0]}")
            print(f"  Name: {result[1]}")
            return True
        else:
            print(f"\nNo product found with ID: {product_id}")
            return False
    except Error as e:
        print(f"Error fetching product info: {e}")
        return False

def update_product(connection, product_id, new_name):
    """Update product name in the database"""
    try:
        cursor = connection.cursor()
        
        # Use parameterized query to prevent SQL injection
        query = "UPDATE products SET name = %s WHERE id = %s"
        cursor.execute(query, (new_name, product_id))
        
        # Get number of rows affected
        rows_updated = cursor.rowcount
        
        # Commit the transaction
        connection.commit()
        
        print(f"\n✓ Successfully updated {rows_updated} row(s)")
        
        cursor.close()
        return rows_updated
        
    except Error as e:
        print(f"Error updating product: {e}")
        connection.rollback()
        return 0

def main():
    """Main function to run the product update"""
    connection = connect_to_database()
    
    if connection is None:
        print("Failed to connect to database. Exiting...")
        return
    
    try:
        while True:
            print("\n" + "="*50)
            choice = input("Update a product? (yes/no): ").strip().lower()
            
            if choice in ['no', 'n', 'quit', 'exit']:
                print("Goodbye!")
                break
            
            if choice not in ['yes', 'y']:
                print("Please enter 'yes' or 'no'")
                continue
            
            # Get product ID
            try:
                product_id = input("\nEnter product ID: ").strip()
                product_id = int(product_id)
            except ValueError:
                print("Invalid product ID. Please enter a number.")
                continue
            
            # Show current product info
            if not get_product_info(connection, product_id):
                continue
            
            # Get new product name
            new_name = input("\nEnter new product name: ").strip()
            
            if not new_name:
                print("Product name cannot be empty")
                continue
            
            # Confirm update
            confirm = input(f"\nConfirm update to '{new_name}'? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                update_product(connection, product_id, new_name)
            else:
                print("Update cancelled")
    
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed")

if __name__ == "__main__":
    main()