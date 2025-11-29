import psycopg2
from psycopg2 import Error, sql
import re
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'shop_database',
    'user': 'your_username',
    'password': 'your_password',
    'port': 5432
}

def validate_product_id(product_id_str):
    """
    Validate that the product ID is a positive integer.
    
    Args:
        product_id_str: String input for product ID
    
    Returns:
        Tuple of (is_valid: bool, product_id: int or None, error_message: str)
    """
    if not product_id_str or not product_id_str.strip():
        return False, None, "Product ID cannot be empty"
    
    try:
        product_id = int(product_id_str.strip())
        
        if product_id <= 0:
            return False, None, "Product ID must be a positive number"
        
        if product_id > 2147483647:  # PostgreSQL INT max
            return False, None, "Product ID is too large"
        
        return True, product_id, None
        
    except ValueError:
        return False, None, "Product ID must be a valid integer"

def validate_product_name(name):
    """
    Validate the product name.
    
    Args:
        name: Product name string
    
    Returns:
        Tuple of (is_valid: bool, cleaned_name: str, error_message: str)
    """
    if not name or not name.strip():
        return False, None, "Product name cannot be empty"
    
    cleaned = name.strip()
    
    # Check length
    if len(cleaned) < 2:
        return False, None, "Product name must be at least 2 characters"
    
    if len(cleaned) > 255:
        return False, None, "Product name is too long (max 255 characters)"
    
    # Check for suspicious patterns (only control characters, no printable text)
    if not any(c.isprintable() and not c.isspace() for c in cleaned):
        return False, None, "Product name must contain printable characters"
    
    # Optional: Check for SQL injection attempts (basic heuristic)
    suspicious_patterns = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+.*\s+SET',
        r'UNION\s+SELECT',
        r'--\s*$',
        r'/\*.*\*/'
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False, None, "Product name contains suspicious content"
    
    return True, cleaned, None

def connect_to_database():
    """
    Establish a secure connection to PostgreSQL database.
    
    Returns:
        Connection object or None if connection fails
    """
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        
        print(f"✓ Successfully connected to PostgreSQL")
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"✓ PostgreSQL version: {db_version.split(',')[0]}")
        cursor.close()
        
        return connection
        
    except Error as e:
        print(f"✗ Error connecting to PostgreSQL: {e}")
        return None

def get_product_info(connection, product_id):
    """
    Retrieve current product information before updating.
    Uses parameterized query for security.
    
    Args:
        connection: PostgreSQL connection object
        product_id: Product ID to retrieve
    
    Returns:
        Dictionary with product info or None if not found
    """
    try:
        cursor = connection.cursor()
        
        # SECURE: Using parameterized query with %s placeholder
        query = """
            SELECT id, name, description, price, category, stock_quantity
            FROM products
            WHERE id = %s
        """
        
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'price': result[3],
                'category': result[4],
                'stock_quantity': result[5]
            }
        
        return None
        
    except Error as e:
        print(f"✗ Error retrieving product: {e}")
        return None

def update_product_name(connection, product_id, new_name):
    """
    Securely update product name using parameterized query.
    
    Args:
        connection: PostgreSQL connection object
        product_id: ID of product to update
        new_name: New name for the product
    
    Returns:
        Number of rows updated or -1 if error
    """
    try:
        cursor = connection.cursor()
        
        # SECURE: Using parameterized UPDATE query with %s placeholders
        # Parameters are passed separately, never concatenated into SQL
        query = """
            UPDATE products 
            SET name = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        # Execute with parameters as tuple
        cursor.execute(query, (new_name, product_id))
        
        # Get number of rows affected
        rows_updated = cursor.rowcount
        
        # Commit the transaction
        connection.commit()
        
        cursor.close()
        
        return rows_updated
        
    except Error as e:
        print(f"✗ Error updating product: {e}")
        connection.rollback()
        return -1

def update_multiple_fields(connection, product_id, updates):
    """
    Securely update multiple product fields.
    Demonstrates dynamic parameterized queries.
    
    Args:
        connection: PostgreSQL connection object
        product_id: ID of product to update
        updates: Dictionary of field names and values
    
    Returns:
        Number of rows updated or -1 if error
    """
    try:
        cursor = connection.cursor()
        
        # Build SET clause dynamically but safely
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)
        
        # Add updated timestamp
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add product_id as final parameter
        params.append(product_id)
        
        # Build complete query
        query = f"""
            UPDATE products 
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """
        
        # SECURE: All values passed as parameters
        cursor.execute(query, tuple(params))
        
        rows_updated = cursor.rowcount
        connection.commit()
        cursor.close()
        
        return rows_updated
        
    except Error as e:
        print(f"✗ Error updating product: {e}")
        connection.rollback()
        return -1

def display_product(product):
    """
    Display product information in a user-friendly format.
    
    Args:
        product: Dictionary containing product data
    """
    print(f"\n{'='*60}")
    print(f"Product ID: {product['id']}")
    print(f"Name: {product['name']}")
    
    if product.get('description'):
        desc = product['description']
        if len(desc) > 100:
            desc = desc[:97] + "..."
        print(f"Description: {desc}")
    
    if product.get('price') is not None:
        print(f"Price: ${float(product['price']):.2f}")
    
    if product.get('category'):
        print(f"Category: {product['category']}")
    
    if product.get('stock_quantity') is not None:
        print(f"Stock: {product['stock_quantity']}")
    
    print('='*60)

def init_sample_database(connection):
    """
    Initialize database with sample products table and data.
    
    Args:
        connection: PostgreSQL connection object
    """
    try:
        cursor = connection.cursor()
        
        # Create products table with updated_at field
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL,
                category VARCHAR(100),
                stock_quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)
        """)
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\nInitializing database with sample products...")
            
            # SECURE: Using parameterized INSERT
            sample_products = [
                ("Laptop Pro 15", "High-performance laptop with 16GB RAM", 1299.99, "Electronics", 15),
                ("Wireless Mouse", "Ergonomic wireless mouse", 29.99, "Electronics", 50),
                ("Office Chair", "Comfortable ergonomic chair", 249.99, "Furniture", 20),
                ("Desk Lamp", "LED desk lamp with adjustable brightness", 39.99, "Furniture", 30),
                ("Python Book", "Learn Python programming", 49.99, "Books", 100),
            ]
            
            insert_query = """
                INSERT INTO products (name, description, price, category, stock_quantity)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_query, sample_products)
            connection.commit()
            
            print(f"✓ Created {len(sample_products)} sample products")
        
        cursor.close()
        
    except Error as e:
        print(f"✗ Error initializing database: {e}")
        connection.rollback()

def demonstrate_sql_injection():
    """
    Demonstrate SQL injection prevention.
    """
    print("\n" + "="*70)
    print("SQL INJECTION PREVENTION DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE APPROACH (vulnerable):")
    print("-" * 70)
    product_id = "1"
    new_name = "Hacked'; DROP TABLE products; --"
    
    insecure_query = f"UPDATE products SET name = '{new_name}' WHERE id = {product_id}"
    print("If we built the query with string formatting:")
    print(f"  {insecure_query}")
    print("\nThis would execute:")
    print("  UPDATE products SET name = 'Hacked';")
    print("  DROP TABLE products; -- WHERE id = 1")
    print("\nThe entire products table would be DELETED!")
    
    print("\n✅ SECURE APPROACH (parameterized):")
    print("-" * 70)
    secure_query = "UPDATE products SET name = %s WHERE id = %s"
    print("Query template with placeholders:")
    print(f"  {secure_query}")
    print("Parameters passed separately:")
    print(f"  ('{new_name}', {product_id})")
    print("\nThe database treats the entire name as data, not SQL code.")
    print("The malicious SQL is stored as a literal string value.")
    print("Your database remains safe!")

def simple_update(connection):
    """
    Perform a simple product name update with full validation.
    """
    print("\n" + "="*60)
    print("UPDATE PRODUCT NAME")
    print("="*60)
    
    # Get product ID
    product_id_str = input("\nEnter Product ID: ").strip()
    
    # Validate product ID
    is_valid, product_id, error = validate_product_id(product_id_str)
    if not is_valid:
        print(f"✗ {error}")
        return
    
    # Get current product info
    print(f"\n✓ Fetching product information...")
    product = get_product_info(connection, product_id)
    
    if not product:
        print(f"✗ No product found with ID: {product_id}")
        return
    
    # Display current product info
    print("\nCurrent product information:")
    display_product(product)
    
    # Get new product name
    new_name = input("\nEnter new product name: ").strip()
    
    # Validate new name
    is_valid, cleaned_name, error = validate_product_name(new_name)
    if not is_valid:
        print(f"✗ {error}")
        return
    
    # Confirm update
    print(f"\nYou are about to change:")
    print(f"  Old name: {product['name']}")
    print(f"  New name: {cleaned_name}")
    
    confirm = input("\nConfirm update? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("✗ Update cancelled")
        return
    
    # Perform the update
    print("\n✓ Updating product...")
    rows_updated = update_product_name(connection, product_id, cleaned_name)
    
    # Report results securely
    print("\n" + "="*60)
    if rows_updated == 1:
        print("✓ UPDATE SUCCESSFUL")
        print(f"✓ {rows_updated} row was modified")
    elif rows_updated == 0:
        print("⚠ UPDATE COMPLETED")
        print("⚠ 0 rows were modified (product may not exist)")
    elif rows_updated > 1:
        print("⚠ UNEXPECTED RESULT")
        print(f"⚠ {rows_updated} rows were modified (expected 1)")
    else:
        print("✗ UPDATE FAILED")
    print("="*60)
    
    # Display updated product
    if rows_updated > 0:
        print("\nUpdated product information:")
        updated_product = get_product_info(connection, product_id)
        if updated_product:
            display_product(updated_product)

def advanced_update(connection):
    """
    Update multiple product fields securely.
    """
    print("\n" + "="*60)
    print("ADVANCED PRODUCT UPDATE")
    print("="*60)
    
    # Get product ID
    product_id_str = input("\nEnter Product ID: ").strip()
    
    is_valid, product_id, error = validate_product_id(product_id_str)
    if not is_valid:
        print(f"✗ {error}")
        return
    
    # Get current product
    product = get_product_info(connection, product_id)
    if not product:
        print(f"✗ No product found with ID: {product_id}")
        return
    
    print("\nCurrent product information:")
    display_product(product)
    
    # Collect updates
    updates = {}
    
    new_name = input("\nNew name (press Enter to skip): ").strip()
    if new_name:
        is_valid, cleaned_name, error = validate_product_name(new_name)
        if is_valid:
            updates['name'] = cleaned_name
        else:
            print(f"✗ Invalid name: {error}")
            return
    
    new_price = input("New price (press Enter to skip): ").strip()
    if new_price:
        try:
            price = float(new_price)
            if price >= 0:
                updates['price'] = price
            else:
                print("✗ Price must be non-negative")
                return
        except ValueError:
            print("✗ Invalid price format")
            return
    
    new_stock = input("New stock quantity (press Enter to skip): ").strip()
    if new_stock:
        try:
            stock = int(new_stock)
            if stock >= 0:
                updates['stock_quantity'] = stock
            else:
                print("✗ Stock must be non-negative")
                return
        except ValueError:
            print("✗ Invalid stock format")
            return
    
    if not updates:
        print("✗ No updates provided")
        return
    
    # Confirm
    print("\nFields to update:")
    for field, value in updates.items():
        print(f"  {field}: {value}")
    
    confirm = input("\nConfirm update? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("✗ Update cancelled")
        return
    
    # Perform update
    rows_updated = update_multiple_fields(connection, product_id, updates)
    
    print("\n" + "="*60)
    if rows_updated == 1:
        print(f"✓ Successfully updated {rows_updated} row")
        print(f"✓ Modified fields: {', '.join(updates.keys())}")
    else:
        print(f"⚠ Updated {rows_updated} rows")
    print("="*60)

def main():
    """Main function for secure product update system"""
    print("="*70)
    print("        SECURE POSTGRESQL PRODUCT UPDATE")
    print("="*70)
    print("\nThis system demonstrates secure database updates using")
    print("parameterized queries to prevent SQL injection attacks.")
    
    # Connect to database
    connection = connect_to_database()
    
    if not connection:
        print("\n✗ Cannot proceed without database connection")
        print("Please check your database configuration in DB_CONFIG")
        return
    
    try:
        # Initialize database
        init_sample_database(connection)
        
        while True:
            print("\n" + "="*60)
            print("OPTIONS:")
            print("  1. Update product name")
            print("  2. Advanced update (multiple fields)")
            print("  3. View product by ID")
            print("  4. Show SQL injection demonstration")
            print("  5. Quit")
            print("="*60)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                simple_update(connection)
            
            elif choice == '2':
                advanced_update(connection)
            
            elif choice == '3':
                product_id_str = input("\nEnter Product ID: ").strip()
                is_valid, product_id, error = validate_product_id(product_id_str)
                if is_valid:
                    product = get_product_info(connection, product_id)
                    if product:
                        display_product(product)
                    else:
                        print(f"✗ No product found with ID: {product_id}")
                else:
                    print(f"✗ {error}")
            
            elif choice == '4':
                demonstrate_sql_injection()
            
            elif choice == '5':
                print("\nGoodbye!")
                break
            
            else:
                print("✗ Invalid option")
    
    finally:
        if connection:
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