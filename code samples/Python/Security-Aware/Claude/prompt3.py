import sqlite3
import hashlib
import getpass
from pathlib import Path

def hash_password(password):
    """
    Hash a password using SHA-256.
    In production, use bcrypt, scrypt, or argon2 instead.
    
    Args:
        password: Plain text password
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_database(db_path='users.db'):
    """
    Initialize the database with a users table and sample data.
    This function creates the database if it doesn't exist.
    
    Args:
        db_path: Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table with parameterized schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if table is empty
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Initializing database with sample users...")
            
            # Insert sample users using parameterized queries
            sample_users = [
                ('admin', 'admin123', 'admin@example.com'),
                ('john_doe', 'password123', 'john@example.com'),
                ('alice', 'secure_pass', 'alice@example.com'),
                ('bob', 'mypassword', 'bob@example.com')
            ]
            
            for username, password, email in sample_users:
                password_hash = hash_password(password)
                # SECURE: Using parameterized query with placeholders
                cursor.execute(
                    'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                    (username, password_hash, email)
                )
            
            conn.commit()
            print(f"Created {len(sample_users)} sample users")
            print("\nSample credentials for testing:")
            for username, password, _ in sample_users:
                print(f"  Username: {username}, Password: {password}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise

def check_login(db_path='users.db'):
    """
    Secure login function using parameterized SQL queries.
    Prompts user for credentials and validates against database.
    
    Args:
        db_path: Path to the SQLite database file
    
    Returns:
        Tuple of (success: bool, username: str or None)
    """
    try:
        # Check if database exists
        if not Path(db_path).exists():
            print(f"Error: Database file '{db_path}' not found")
            print("Run init_database() first to create the database")
            return False, None
        
        # Prompt for credentials
        print("\n" + "="*50)
        print("           LOGIN")
        print("="*50)
        username = input("Username: ").strip()
        
        # Use getpass to hide password input
        password = getpass.getpass("Password: ")
        
        # Validate input
        if not username or not password:
            print("\n✗ Error: Username and password cannot be empty")
            return False, None
        
        # Hash the provided password
        password_hash = hash_password(password)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SECURE: Using parameterized query with ? placeholders
        # This prevents SQL injection attacks
        query = '''
            SELECT id, username, email 
            FROM users 
            WHERE username = ? AND password_hash = ?
        '''
        
        # Execute with parameters as a tuple
        cursor.execute(query, (username, password_hash))
        
        # Fetch result
        result = cursor.fetchone()
        
        conn.close()
        
        # Check if login was successful
        if result:
            user_id, username, email = result
            print("\n" + "="*50)
            print("✓ LOGIN SUCCESSFUL")
            print("="*50)
            print(f"Welcome back, {username}!")
            print(f"User ID: {user_id}")
            print(f"Email: {email}")
            return True, username
        else:
            print("\n" + "="*50)
            print("✗ LOGIN FAILED")
            print("="*50)
            print("Invalid username or password")
            return False, None
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return False, None
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False, None

def demonstrate_sql_injection():
    """
    Demonstrate why parameterized queries are necessary.
    Shows what WOULD happen with insecure string concatenation.
    """
    print("\n" + "="*70)
    print("SQL INJECTION DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE (vulnerable to SQL injection):")
    print("=" * 70)
    username = "admin"
    password = "' OR '1'='1"
    
    # This is what you should NEVER do:
    insecure_query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print("Query built with string formatting:")
    print(f"  {insecure_query}")
    print("\nThis query would return ALL users because '1'='1' is always true!")
    print("An attacker could log in as any user without knowing the password.")
    
    print("\n✅ SECURE (using parameterized queries):")
    print("=" * 70)
    secure_query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
    print("Query with placeholders:")
    print(f"  {secure_query}")
    print("Parameters passed separately:")
    print(f"  ('{username}', '{hash_password(password)}')")
    print("\nThe database treats the entire input as data, not SQL code.")
    print("Special characters are properly escaped automatically.")

def add_user(db_path='users.db'):
    """
    Securely add a new user to the database.
    Demonstrates parameterized INSERT queries.
    
    Args:
        db_path: Path to the SQLite database file
    """
    try:
        print("\n" + "="*50)
        print("     ADD NEW USER")
        print("="*50)
        
        username = input("New username: ").strip()
        password = getpass.getpass("New password: ")
        email = input("Email address: ").strip()
        
        if not username or not password:
            print("\n✗ Username and password are required")
            return False
        
        password_hash = hash_password(password)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SECURE: Parameterized INSERT query
        cursor.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
            (username, password_hash, email)
        )
        
        conn.commit()
        conn.close()
        
        print(f"\n✓ User '{username}' created successfully")
        return True
        
    except sqlite3.IntegrityError:
        print(f"\n✗ Error: Username '{username}' already exists")
        return False
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return False

def main():
    """Main function demonstrating the secure login system"""
    db_path = 'users.db'
    
    print("="*70)
    print("        SECURE LOGIN SYSTEM DEMONSTRATION")
    print("="*70)
    
    # Initialize database if needed
    if not Path(db_path).exists():
        print("\nDatabase not found. Creating new database...")
        init_database(db_path)
    
    while True:
        print("\n" + "="*70)
        print("OPTIONS:")
        print("  1. Login")
        print("  2. Add new user")
        print("  3. Show SQL injection demonstration")
        print("  4. Reinitialize database")
        print("  5. Quit")
        print("="*70)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            success, username = check_login(db_path)
            if success:
                print(f"\nYou are now logged in as {username}")
        
        elif choice == '2':
            add_user(db_path)
        
        elif choice == '3':
            demonstrate_sql_injection()
        
        elif choice == '4':
            confirm = input("This will delete all users. Continue? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                Path(db_path).unlink(missing_ok=True)
                init_database(db_path)
        
        elif choice == '5':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")