import mysql.connector
from mysql.connector import Error

def connect_to_database():
    """Establish connection to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='your_database_name',
            user='your_username',
            password='your_password'
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database\n")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def search_products(connection, keyword):
    """Search for products by keyword in name or description"""
    try:
        cursor = connection.cursor()
        
        # Use parameterized query to prevent SQL injection
        query = """
            SELECT name, price 
            FROM products 
            WHERE name LIKE %s OR description LIKE %s
            ORDER BY name
        """
        
        # Add wildcards for pattern matching
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\nFound {len(results)} product(s) matching '{keyword}':\n")
            print(f"{'Product Name':<40} {'Price':>10}")
            print("-" * 52)
            for name, price in results:
                print(f"{name:<40} ${price:>9.2f}")
        else:
            print(f"\nNo products found matching '{keyword}'")
        
        cursor.close()
        
    except Error as e:
        print(f"Error executing query: {e}")

def main():
    """Main function to run the product search"""
    connection = connect_to_database()
    
    if connection is None:
        print("Failed to connect to database. Exiting...")
        return
    
    try:
        while True:
            keyword = input("\nEnter a keyword to search for products (or 'quit' to exit): ").strip()
            
            if keyword.lower() == 'quit':
                print("Goodbye!")
                break
            
            if not keyword:
                print("Please enter a valid keyword")
                continue
            
            search_products(connection, keyword)
    
    finally:
        if connection.is_connected():
            connection.close()
            print("\nDatabase connection closed")

if __name__ == "__main__":
    main()