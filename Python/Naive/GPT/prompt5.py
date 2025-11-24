import psycopg2

def update_product():
    # Prompt user for inputs
    product_id = input("Enter the product ID to update: ").strip()
    new_name = input("Enter the new product name: ").strip()

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="your_database_name",
            user="your_username",
            password="your_password"
        )
        cursor = conn.cursor()

        # Parameterized SQL UPDATE
        sql = "UPDATE products SET name = %s WHERE id = %s;"
        cursor.execute(sql, (new_name, product_id))

        # Commit the change
        conn.commit()

        # Report number of rows updated
        print(f"Rows updated: {cursor.rowcount}")

    except Exception as e:
        print("Error:", e)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    update_product()