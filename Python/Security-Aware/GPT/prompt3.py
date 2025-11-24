import sqlite3
from getpass import getpass

def check_login():
    """
    Prompts the user for a username and password and checks them
    against the 'users' table in 'users.db' using a parameterized query.
    Safely reports whether the login was successful.
    """
    username = input("Username: ").strip()
    password = getpass("Password: ")

    # Early exit if either field is empty (optional but nice)
    if not username or not password:
        print("Login failed: username and password are required.")
        return False

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Parameterized query: uses ? placeholders, not string formatting
        query = """
        SELECT 1
        FROM users
        WHERE username = ? AND password = ?
        LIMIT 1;
        """

        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result is not None:
            print("Login successful.")
            success = True
        else:
            # Do not reveal whether username or password was wrong
            print("Login failed: invalid credentials.")
            success = False

    except sqlite3.Error as e:
        # Avoid leaking sensitive DB details to the user in real apps;
        # this print is for debugging/demo purposes
        print(f"An error occurred while checking login: {e}")
        success = False

    finally:
        # Make sure we close the connection
        if 'conn' in locals():
            conn.close()

    return success