import mysql.connector
from mysql.connector import Error
import re
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'shop_database',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306
}

def validate_keyword(keyword):
    """
    Validate the search keyword.
    
    Args:
        keyword: Search term to validate
    
    Returns:
        Tuple of (is_valid: bool, cleaned_keyword: str, error_message: str)
    """
    # Check if keyword is empty
    if not keyword or not keyword.strip():
        return False, None, "Search keyword cannot be empty"
    
    # Clean the keyword
    cleaned = keyword.strip()
    
    # Check length (prevent excessively long searches)
    if len(cleaned) > 100:
        return False, None, "Search keyword is too long (max 100 characters)"
    
    # Check for minimum length
    if len(cleaned) < 2:
        return False, None, "Search keyword must be at least 2 characters"
    
    # Optional: Check for suspicious patterns (too many special characters)
    special_char_count = len(re.findall(r'[^a-zA-Z0-9\s]', cleaned))
    if special_char_count > len(cleaned) * 0.5:
        return False, None, "Search keyword contains too many special characters"
    
    return True, cleaned, None

def connect_to_database():
    """
    Establish a secure connection to MySQL database.
    
    Returns:
        Connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✓ Successfully connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"✓ Connected to database: {db_name}\n")
            cursor.close()
            
            return connection
        
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def search_products(connection, keyword):
    """
    Securely search for products using parameterized queries.
    
    Args:
        connection: MySQL connection object
        keyword: Validated search keyword
    
    Returns:
        List of product dictionaries or None if error
    """
    try:
        cursor = connection.cursor(dictionary=True)
        
        # SECURE: Using parameterized query with %s placeholders
        # The % wildcards are added in the parameter values, NOT in the query string
        query = """
            SELECT 
                id,
                name,
                description,
                price,
                category,
                stock_quantity,
                created_at
            FROM products 
            WHERE 
                name LIKE %s 
                OR description LIKE %s
            ORDER BY name
            LIMIT 50
        """
        
        # Add wildcards to the search term for LIKE matching
        search_pattern = f"%{keyword}%"
        
        # Execute with parameters - this prevents SQL injection
        cursor.execute(query, (search_pattern, search_pattern))
        
        results = cursor.fetchall()
        cursor.close()
        
        return results
        
    except Error as e:
        print(f"✗ Database query error: {e}")
        return None

def display_results(results, keyword):
    """
    Display search results in a secure and user-friendly format.
    
    Args:
        results: List of product dictionaries
        keyword: The search keyword used
    """
    if not results:
        print(f"\n{'='*70}")
        print(f"No products found matching '{keyword}'")
        print('='*70)
        return
    
    print(f"\n{'='*70}")
    print(f"Found {len(results)} product(s) matching '{keyword}'")
    print('='*70)
    
    for i, product in enumerate(results, 1):
        print(f"\n{i}. {product['name']}")
        print("-" * 70)
        
        # Safely display description (truncate if too long)
        description = product.get('description', 'No description')
        if description and len(description) > 100:
            description = description[:97] + "..."
        print(f"   Description: {description}")
        
        # Format price safely
        price = product.get('price')
        if price is not None:
            print(f"   Price: ${float(price):.2f}")
        else:
            print(f"   Price: N/A")
        
        # Display other fields
        category = product.get('category', 'Uncategorized')
        print(f"   Category: {category}")
        
        stock = product.get('stock_quantity', 0)
        stock_status = "In Stock" if stock > 0 else "Out of Stock"
        print(f"   Stock: {stock} ({stock_status})")
        
        # Display product ID (useful for further operations)
        print(f"   Product ID: {product['id']}")
    
    print("\n" + "="*70)

def init_sample_database(connection):
    """
    Initialize database with sample products table and data.
    This is for demonstration purposes only.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                category VARCHAR(100),
                stock_quantity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_name (name),
                INDEX idx_category (category)
            )
        """)
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Initializing database with sample products...")
            
            # Insert sample products using parameterized queries
            sample_products = [
                ("Laptop Pro 15", "High-performance laptop with 16GB RAM", 1299.99, "Electronics", 15),
                ("Wireless Mouse", "Ergonomic wireless mouse with USB receiver", 29.99, "Electronics", 50),
                ("Office Chair", "Comfortable ergonomic office chair", 249.99, "Furniture", 20),
                ("Desk Lamp", "LED desk lamp with adjustable brightness", 39.99, "Furniture", 30),
                ("Python Programming Book", "Learn Python from scratch", 49.99, "Books", 100),
                ("Coffee Maker", "Automatic coffee maker with timer", 89.99, "Appliances", 25),
                ("Bluetooth Headphones", "Noise-canceling wireless headphones", 149.99, "Electronics", 40),
                ("Standing Desk", "Adjustable height standing desk", 399.99, "Furniture", 10),
                ("Mechanical Keyboard", "RGB mechanical gaming keyboard", 119.99, "Electronics", 35),
                ("Water Bottle", "Insulated stainless steel water bottle", 24.99, "Accessories", 200)
            ]
            
            # SECURE: Using parameterized INSERT
            insert_query = """
                INSERT INTO products (name, description, price, category, stock_quantity)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, sample_products)
            connection.commit()
            
            print(f"✓ Created {len(sample_products)} sample products\n")
        
        cursor.close()
        
    except Error as e:
        print(f"✗ Error initializing database: {e}")

def demonstrate_sql_injection():
    """
    Demonstrate why parameterized queries are essential.
    """
    print("\n" + "="*70)
    print("SQL INJECTION PREVENTION DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE APPROACH (vulnerable):")
    print("-" * 70)
    keyword = "laptop' OR '1'='1"
    insecure_query = f"SELECT * FROM products WHERE name LIKE '%{keyword}%'"
    print("If we built the query with string formatting:")
    print(f"  {insecure_query}")
    print("\nThis would return ALL products because '1'='1' is always true!")
    print("An attacker could extract all data or even modify/delete records.")
    
    print("\n✅ SECURE APPROACH (parameterized):")
    print("-" * 70)
    secure_query = "SELECT * FROM products WHERE name LIKE %s"
    search_pattern = f"%{keyword}%"
    print("Query template with placeholder:")
    print(f"  {secure_query}")
    print("Parameter passed separately:")
    print(f"  ('{search_pattern}',)")
    print("\nThe database treats the entire input as data, not SQL code.")
    print("Special characters are automatically escaped by the driver.")
    print("The malicious input is treated as a literal search term.")

def advanced_search(connection):
    """
    Perform an advanced search with multiple criteria.
    Demonstrates complex parameterized queries.
    """
    print("\n" + "="*70)
    print("ADVANCED SEARCH")
    print("="*70)
    
    keyword = input("Product keyword: ").strip()
    category = input("Category (leave empty for all): ").strip()
    max_price_str = input("Maximum price (leave empty for no limit): ").strip()
    
    # Validate keyword
    is_valid, cleaned_keyword, error = validate_keyword(keyword)
    if not is_valid:
        print(f"✗ {error}")
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Build query dynamically but safely
        query = """
            SELECT id, name, description, price, category, stock_quantity
            FROM products 
            WHERE (name LIKE %s OR description LIKE %s)
        """
        
        params = [f"%{cleaned_keyword}%", f"%{cleaned_keyword}%"]
        
        # Add category filter if provided
        if category:
            query += " AND category = %s"
            params.append(category)
        
        # Add price filter if provided
        if max_price_str:
            try:
                max_price = float(max_price_str)
                query += " AND price <= %s"
                params.append(max_price)
            except ValueError:
                print("✗ Invalid price format, ignoring price filter")
        
        query += " ORDER BY name LIMIT 50"
        
        # SECURE: All parameters passed as tuple
        cursor.execute(query, tuple(params))
        
        results = cursor.fetchall()
        cursor.close()
        
        display_results(results, cleaned_keyword)
        
    except Error as e:
        print(f"✗ Database error: {e}")

def main():
    """Main function for the secure product search system"""
    print("="*70)
    print("        SECURE MYSQL PRODUCT SEARCH")
    print("="*70)
    print("\nThis system demonstrates secure database queries using")
    print("parameterized statements to prevent SQL injection attacks.")
    
    # Connect to database
    connection = connect_to_database()
    
    if not connection:
        print("\n✗ Cannot proceed without database connection")
        print("Please check your database configuration in DB_CONFIG")
        return
    
    try:
        # Initialize database with sample data if needed
        init_sample_database(connection)
        
        while True:
            print("\n" + "="*70)
            print("OPTIONS:")
            print("  1. Search products")
            print("  2. Advanced search (with filters)")
            print("  3. Show SQL injection demonstration")
            print("  4. Quit")
            print("="*70)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                print("\n" + "="*70)
                print("PRODUCT SEARCH")
                print("="*70)
                
                keyword = input("\nEnter search keyword: ").strip()
                
                # Validate the keyword
                is_valid, cleaned_keyword, error = validate_keyword(keyword)
                
                if not is_valid:
                    print(f"\n✗ Validation error: {error}")
                    continue
                
                print(f"\n✓ Searching for products matching '{cleaned_keyword}'...")
                
                # Perform secure search
                results = search_products(connection, cleaned_keyword)
                
                if results is not None:
                    display_results(results, cleaned_keyword)
            
            elif choice == '2':
                advanced_search(connection)
            
            elif choice == '3':
                demonstrate_sql_injection()
            
            elif choice == '4':
                print("\nGoodbye!")
                break
            
            else:
                print("✗ Invalid option, please try again")
    
    finally:
        # Always close the connection
        if connection and connection.is_connected():
            connection.close()
            print("\n✓ Database connection closed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)