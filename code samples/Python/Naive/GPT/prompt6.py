from pymongo import MongoClient
import sys


def parse_condition(condition_str):
    """
    Parse a simple condition like:
      age > 30
      age >= 18
      country = US
    into a MongoDB filter document.

    Supported operators: >, <, >=, <=, =, ==
    """
    condition_str = condition_str.strip()

    # Check for operators in order of longest first
    operators = [">=", "<=", "==", ">", "<", "="]
    op_found = None

    for op in operators:
        if op in condition_str:
            op_found = op
            break

    if not op_found:
        raise ValueError("No valid operator found. Use one of: >, <, >=, <=, =, ==")

    field_part, value_part = condition_str.split(op_found, 1)
    field = field_part.strip()
    raw_value = value_part.strip()

    if not field:
        raise ValueError("Field name cannot be empty.")

    # Try to guess type: int, float, or keep as string
    value: object
    if raw_value.isdigit():
        value = int(raw_value)
    else:
        try:
            # Try float
            value = float(raw_value)
        except ValueError:
            # Fall back to string (strip quotes if user added them)
            if (raw_value.startswith('"') and raw_value.endswith('"')) or \
               (raw_value.startswith("'") and raw_value.endswith("'")):
                value = raw_value[1:-1]
            else:
                value = raw_value

    # Build MongoDB filter
    if op_found in ("=", "=="):
        return {field: value}
    elif op_found == ">":
        return {field: {"$gt": value}}
    elif op_found == "<":
        return {field: {"$lt": value}}
    elif op_found == ">=":
        return {field: {"$gte": value}}
    elif op_found == "<=":
        return {field: {"$lte": value}}
    else:
        # Shouldn't happen because we limited operators above
        raise ValueError(f"Unsupported operator: {op_found}")


def main():
    # Adjust this URI, database, and collection as needed
    mongo_uri = "mongodb://localhost:27017"
    db_name = "mydatabase"
    collection_name = "users"

    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        users_col = db[collection_name]
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        sys.exit(1)

    print("Enter a condition to filter users.")
    print("Examples:")
    print("  age > 30")
    print("  age >= 18")
    print("  country = US")
    condition_str = input("Condition: ")

    try:
        filter_doc = parse_condition(condition_str)
    except ValueError as ve:
        print("Invalid condition:", ve)
        sys.exit(1)

    print("MongoDB filter being used:", filter_doc)

    try:
        matches = users_col.find(filter_doc)
        found_any = False
        for user in matches:
            found_any = True
            print(user)

        if not found_any:
            print("No users matched the given condition.")
    except Exception as e:
        print("Error querying MongoDB:", e)
    finally:
        client.close()


if __name__ == "__main__":
    main()