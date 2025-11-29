import sqlite3
import getpass
import os

DB_NAME = "users.db"

def setup_database():
    """
    Creates a dummy database and user for demonstration purposes.
    In a real app, passwords should be hashed (e.g., bcrypt/Argon2) 
    before storage, not stored as plain text.
    """
    if os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert a sample user
    # Note: We use parameterized queries here too for consistency
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  ("admin", "secret123"))
    
    conn.commit()
    conn.close()
    print(f"[-] Database '{DB_NAME}' created with sample user 'admin' / 'secret123'")

def check_login():
    """
    Prompts for credentials and validates them using secure parameterized queries.
    """
    print("\n--- Secure Login System ---")
    
    username = input("Username: ").strip()
    # getpass hides the input characters for security
    password = getpass.getpass("Password: ").strip()

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # --- VULNERABLE CODE (Do NOT do this) ---
        # query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        # cursor.execute(query)
        
        # --- SECURE CODE (Do this) ---
        # We use '?' as placeholders. The database driver handles escaping,
        # treating inputs strictly as data, not executable code.
        query = "SELECT id, username FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        if user:
            print(f"\n[SUCCESS] Welcome back, {user[1]}!")
            return True
        else:
            print("\n[FAILURE] Invalid username or password.")
            return False

    except sqlite3.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
    check_login()