import sqlite3
import getpass

def check_login():
    # Ask the user for credentials
    username = input("Username: ")
    password = getpass.getpass("Password: ")  # hides input; use input() if you prefer

    # Connect to the SQLite database file
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Construct the SQL query using placeholders, then supply the values separately
    # This is safer than concatenating the values directly into the string.
    query = """
        SELECT 1
        FROM users
        WHERE username = ? AND password = ?
        LIMIT 1;
    """

    cursor.execute(query, (username, password))
    row = cursor.fetchone()

    if row is not None:
        print("Login successful.")
    else:
        print("Login failed: invalid username or password.")

    # Clean up
    cursor.close()
    conn.close()