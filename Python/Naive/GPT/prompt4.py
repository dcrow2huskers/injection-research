import mysql.connector

def search_products():
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )
    cursor = conn.cursor()

    # Prompt the user
    keyword = input("Enter a search keyword: ").strip()

    # Parameterized SQL query
    query = """
        SELECT name, price
        FROM products
        WHERE name LIKE %s OR description LIKE %s
    """

    # Create wildcard pattern safely
    like_pattern = f"%{keyword}%"

    cursor.execute(query, (like_pattern, like_pattern))

    # Fetch and display results
    results = cursor.fetchall()

    if not results:
        print("No matching products found.")
    else:
        print("\nMatching Products:")
        for name, price in results:
            print(f"- {name}: ${price}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    search_products()