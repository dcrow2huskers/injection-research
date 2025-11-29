from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import json

def connect_to_database():
    """Establish connection to MongoDB database"""
    try:
        # Update with your MongoDB connection string
        client = MongoClient(
            'mongodb://localhost:27017/',
            serverSelectionTimeoutMS=5000
        )
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB\n")
        
        # Access database and collection
        db = client['your_database_name']
        collection = db['users']
        
        return collection
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_condition(condition_str):
    """
    Parse user input into a MongoDB query condition.
    Supports simple conditions like:
    - age > 25
    - country == USA
    - age >= 18
    - name == John
    """
    condition_str = condition_str.strip()
    
    # Define operators
    operators = {
        '>=': '$gte',
        '<=': '$lte',
        '>': '$gt',
        '<': '$lt',
        '==': '$eq',
        '!=': '$ne'
    }
    
    # Find which operator is used
    op_found = None
    mongo_op = None
    for op, mongo_equiv in operators.items():
        if op in condition_str:
            op_found = op
            mongo_op = mongo_equiv
            break
    
    if not op_found:
        print("Invalid condition format. Use operators: >, <, >=, <=, ==, !=")
        return None
    
    # Split by operator
    parts = condition_str.split(op_found)
    if len(parts) != 2:
        print("Invalid condition format")
        return None
    
    field = parts[0].strip()
    value = parts[1].strip()
    
    # Try to convert value to appropriate type
    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    else:
        # Try to convert to number
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            # Keep as string
            pass
    
    # Build MongoDB query
    if mongo_op == '$eq':
        # For equality, we can use shorthand
        query = {field: value}
    else:
        query = {field: {mongo_op: value}}
    
    return query

def search_users(collection, query):
    """Search for users matching the query"""
    try:
        results = list(collection.find(query))
        
        if results:
            print(f"\nFound {len(results)} user(s) matching the condition:\n")
            print("="*70)
            for i, user in enumerate(results, 1):
                print(f"\nUser {i}:")
                for key, value in user.items():
                    if key != '_id':  # Skip MongoDB's internal ID
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {str(value)}")
                print("-"*70)
        else:
            print("\nNo users found matching the condition")
        
        return len(results)
        
    except OperationFailure as e:
        print(f"Error executing query: {e}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0

def show_examples():
    """Display example queries"""
    print("\nExample conditions:")
    print("  age > 25")
    print("  age >= 18")
    print("  country == USA")
    print("  name == John")
    print("  salary < 50000")
    print("  status != active")

def main():
    """Main function to run the user filter"""
    collection = connect_to_database()
    
    if collection is None:
        print("Failed to connect to database. Exiting...")
        return
    
    print("MongoDB User Filter")
    print("="*70)
    show_examples()
    
    try:
        while True:
            print("\n" + "="*70)
            condition = input("\nEnter a condition to filter users (or 'quit' to exit, 'help' for examples): ").strip()
            
            if condition.lower() == 'quit':
                print("Goodbye!")
                break
            
            if condition.lower() == 'help':
                show_examples()
                continue
            
            if not condition:
                print("Please enter a valid condition")
                continue
            
            # Parse the condition
            query = parse_condition(condition)
            
            if query is None:
                continue
            
            print(f"\nMongoDB query: {json.dumps(query, indent=2)}")
            
            # Execute search
            search_users(collection, query)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()