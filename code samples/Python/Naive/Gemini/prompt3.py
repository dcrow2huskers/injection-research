import sqlite3
import getpass
import os

def setup_database():
    """
    Creates a sample database 'users.db' with a 'users' table
    and some dummy data for testing purposes.
    """
    if os.path.exists('users.db'):
        os.remove('users.db')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE users (
            username TEXT,
            password TEXT
        )
    ''')
    
    # Insert dummy users
    users = [
        ('admin', 'secret123'),
        ('guest', 'guestpass'),
        ('jdoe', 'password')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?)', users)
    
    conn.commit()
    conn.close()
    print("Defaut database 'users.db' created/reset with sample users: admin, guest, jdoe")

def check_login():
    print("\n--- Login Check ---")
    
    # 1. Get user input
    username = input("Enter Username: ").strip()
    # getpass hides the input characters for security
    password = getpass.getpass("Enter Password: ").strip()

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # 2. Construct the SQL Query (SECURELY)
        # We use '?' as placeholders for variables. This is a Parameterized Query.
        # It prevents SQL Injection because the database driver treats the inputs
        # strictly as data, not executable SQL code.
        sql_query = "SELECT * FROM users WHERE username = ? AND password = ?"
        
        # 3. Execute the query
        cursor.execute(sql_query, (username, password))
        
        # Check if a row was returned
        user = cursor.fetchone()
        
        print("-" * 30)
        if user:
            print(f"Success! Access granted for user: {username}")
        else:
            print("Failure! Invalid username or password.")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
    check_login()