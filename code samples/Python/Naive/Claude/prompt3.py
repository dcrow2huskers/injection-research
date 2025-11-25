import sqlite3

def check_login():
    """
    Check user login credentials against a SQLite database.
    WARNING: This implementation is vulnerable to SQL injection attacks!
    """
    # Get username and password from user
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Construct SQL query by concatenating user input (VULNERABLE!)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    print(f"Executing query: {query}")
    
    try:
        # Execute the query
        cursor.execute(query)
        result = cursor.fetchone()
        
        # Check if a matching user was found
        if result:
            print("Login successful!")
            return True
        else:
            print("Login failed: Invalid username or password")
            return False
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    
    finally:
        conn.close()


def check_login_secure():
    """
    SECURE version using parameterized queries.
    This is how you SHOULD implement login functionality.
    """
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Use parameterized query (SECURE!)
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    
    try:
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        
        if result:
            print("Login successful!")
            return True
        else:
            print("Login failed: Invalid username or password")
            return False
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    
    finally:
        conn.close()


# Example: Create a test database
def setup_test_database():
    """Create a sample users table for testing."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert sample users
    cursor.execute("DELETE FROM users")  # Clear existing data
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                   ("admin", "admin123"))
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                   ("user1", "pass456"))
    
    conn.commit()
    conn.close()
    print("Test database created with sample users")


if __name__ == "__main__":
    # Uncomment to set up test database:
    # setup_test_database()
    
    print("=== VULNERABLE VERSION ===")
    check_login()
    
    # Try the SQL injection: admin' OR '1'='1
    
    print("\n=== SECURE VERSION ===")
    # check_login_secure()