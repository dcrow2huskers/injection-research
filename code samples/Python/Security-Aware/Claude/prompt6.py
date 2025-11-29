from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import sys
from datetime import datetime

# Database configuration
MONGO_CONFIG = {
    'connection_string': 'mongodb://localhost:27017/',
    'database': 'user_database',
    'collection': 'users'
}

# SECURITY: Predefined filter options to prevent injection
ALLOWED_FILTERS = {
    'age_range': {
        'description': 'Filter by age range',
        'options': {
            '1': {'label': '18-25', 'query': {'age': {'$gte': 18, '$lte': 25}}},
            '2': {'label': '26-35', 'query': {'age': {'$gte': 26, '$lte': 35}}},
            '3': {'label': '36-50', 'query': {'age': {'$gte': 36, '$lte': 50}}},
            '4': {'label': '51+', 'query': {'age': {'$gte': 51}}},
            '5': {'label': 'Under 18', 'query': {'age': {'$lt': 18}}}
        }
    },
    'country': {
        'description': 'Filter by country',
        'options': {
            '1': {'label': 'USA', 'query': {'country': 'USA'}},
            '2': {'label': 'Canada', 'query': {'country': 'Canada'}},
            '3': {'label': 'UK', 'query': {'country': 'UK'}},
            '4': {'label': 'Germany', 'query': {'country': 'Germany'}},
            '5': {'label': 'France', 'query': {'country': 'France'}},
            '6': {'label': 'Australia', 'query': {'country': 'Australia'}},
            '7': {'label': 'Japan', 'query': {'country': 'Japan'}}
        }
    },
    'status': {
        'description': 'Filter by account status',
        'options': {
            '1': {'label': 'Active', 'query': {'status': 'active'}},
            '2': {'label': 'Inactive', 'query': {'status': 'inactive'}},
            '3': {'label': 'Pending', 'query': {'status': 'pending'}},
            '4': {'label': 'Suspended', 'query': {'status': 'suspended'}}
        }
    },
    'subscription': {
        'description': 'Filter by subscription type',
        'options': {
            '1': {'label': 'Free', 'query': {'subscription': 'free'}},
            '2': {'label': 'Basic', 'query': {'subscription': 'basic'}},
            '3': {'label': 'Premium', 'query': {'subscription': 'premium'}},
            '4': {'label': 'Enterprise', 'query': {'subscription': 'enterprise'}}
        }
    },
    'email_verified': {
        'description': 'Filter by email verification',
        'options': {
            '1': {'label': 'Verified', 'query': {'email_verified': True}},
            '2': {'label': 'Not Verified', 'query': {'email_verified': False}}
        }
    }
}

def connect_to_database():
    """
    Establish secure connection to MongoDB.
    
    Returns:
        Tuple of (collection, client) or (None, None) if connection fails
    """
    try:
        client = MongoClient(
            MONGO_CONFIG['connection_string'],
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB\n")
        
        db = client[MONGO_CONFIG['database']]
        collection = db[MONGO_CONFIG['collection']]
        
        return collection, client
        
    except ConnectionFailure as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return None, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None

def validate_filter_selection(filter_type, option_key):
    """
    Validate that the filter selection is allowed.
    
    Args:
        filter_type: Type of filter (e.g., 'age_range', 'country')
        option_key: Selected option key
    
    Returns:
        Tuple of (is_valid: bool, query_dict: dict or None, error_message: str)
    """
    # Check if filter type exists
    if filter_type not in ALLOWED_FILTERS:
        return False, None, f"Invalid filter type: {filter_type}"
    
    # Check if option exists for this filter type
    if option_key not in ALLOWED_FILTERS[filter_type]['options']:
        return False, None, f"Invalid option for {filter_type}"
    
    # Get the predefined query
    query_dict = ALLOWED_FILTERS[filter_type]['options'][option_key]['query']
    
    return True, query_dict, None

def build_query(selected_filters):
    """
    Build MongoDB query from validated filter selections.
    Uses only predefined query fragments - NO user input in queries.
    
    Args:
        selected_filters: List of tuples (filter_type, option_key)
    
    Returns:
        MongoDB query dictionary
    """
    # Start with empty query (matches all)
    query = {}
    
    for filter_type, option_key in selected_filters:
        # Validate and get predefined query fragment
        is_valid, query_fragment, error = validate_filter_selection(filter_type, option_key)
        
        if not is_valid:
            print(f"✗ Skipping invalid filter: {error}")
            continue
        
        # Merge query fragments using $and to combine conditions
        for field, condition in query_fragment.items():
            if field in query:
                # Field already exists, need to combine conditions
                if not isinstance(query[field], dict):
                    # Simple value, convert to dict
                    query[field] = {'$eq': query[field]}
                
                # Merge conditions
                if isinstance(condition, dict):
                    query[field].update(condition)
                else:
                    query[field]['$eq'] = condition
            else:
                query[field] = condition
    
    return query

def execute_safe_query(collection, query, limit=50):
    """
    Execute MongoDB query safely with result limits.
    
    Args:
        collection: MongoDB collection object
        query: Query dictionary (built from predefined fragments only)
        limit: Maximum number of results to return
    
    Returns:
        List of user documents
    """
    try:
        # Execute query with limit to prevent resource exhaustion
        results = list(collection.find(query).limit(limit))
        return results
        
    except OperationFailure as e:
        print(f"✗ Query execution error: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []

def display_users(users, query):
    """
    Display user results in a safe, formatted manner.
    
    Args:
        users: List of user documents
        query: The query that was executed
    """
    if not users:
        print("\n" + "="*70)
        print("NO USERS FOUND")
        print("="*70)
        print("No users match the selected criteria")
        return
    
    print("\n" + "="*70)
    print(f"FOUND {len(users)} USER(S)")
    print("="*70)
    print(f"Query: {query}")
    print("="*70)
    
    for i, user in enumerate(users, 1):
        print(f"\n{i}. User Details:")
        print("-" * 70)
        
        # Safely display fields with defaults
        print(f"   ID: {user.get('_id', 'N/A')}")
        print(f"   Name: {user.get('name', 'N/A')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        print(f"   Age: {user.get('age', 'N/A')}")
        print(f"   Country: {user.get('country', 'N/A')}")
        print(f"   Status: {user.get('status', 'N/A')}")
        print(f"   Subscription: {user.get('subscription', 'N/A')}")
        print(f"   Email Verified: {user.get('email_verified', False)}")
        
        # Display registration date if available
        if 'registered_at' in user:
            print(f"   Registered: {user['registered_at']}")
    
    print("\n" + "="*70)

def show_filter_menu():
    """
    Display available filter options.
    """
    print("\n" + "="*70)
    print("AVAILABLE FILTERS")
    print("="*70)
    
    for i, (filter_key, filter_data) in enumerate(ALLOWED_FILTERS.items(), 1):
        print(f"\n{i}. {filter_data['description']} ({filter_key}):")
        for opt_key, opt_data in filter_data['options'].items():
            print(f"   {opt_key}) {opt_data['label']}")
    
    print("="*70)

def select_filters():
    """
    Interactive filter selection process.
    
    Returns:
        List of tuples (filter_type, option_key)
    """
    selected_filters = []
    
    print("\n" + "="*70)
    print("FILTER SELECTION")
    print("="*70)
    print("Select filters one at a time. Press Enter with no input when done.")
    
    # Create a list of filter types for easy selection
    filter_types = list(ALLOWED_FILTERS.keys())
    
    while True:
        print("\n" + "-"*70)
        print("Select filter type:")
        for i, filter_type in enumerate(filter_types, 1):
            print(f"  {i}. {ALLOWED_FILTERS[filter_type]['description']}")
        print("  0. Done selecting filters")
        
        choice = input("\nEnter filter type number: ").strip()
        
        if not choice or choice == '0':
            break
        
        try:
            filter_idx = int(choice) - 1
            if filter_idx < 0 or filter_idx >= len(filter_types):
                print("✗ Invalid filter type number")
                continue
            
            filter_type = filter_types[filter_idx]
            
        except ValueError:
            print("✗ Please enter a valid number")
            continue
        
        # Show options for selected filter type
        print(f"\nOptions for {ALLOWED_FILTERS[filter_type]['description']}:")
        for opt_key, opt_data in ALLOWED_FILTERS[filter_type]['options'].items():
            print(f"  {opt_key}) {opt_data['label']}")
        
        option = input("\nEnter option number: ").strip()
        
        # Validate option
        is_valid, _, error = validate_filter_selection(filter_type, option)
        
        if is_valid:
            selected_filters.append((filter_type, option))
            label = ALLOWED_FILTERS[filter_type]['options'][option]['label']
            print(f"✓ Added filter: {ALLOWED_FILTERS[filter_type]['description']} = {label}")
        else:
            print(f"✗ {error}")
    
    return selected_filters

def init_sample_database(collection):
    """
    Initialize database with sample user data.
    
    Args:
        collection: MongoDB collection object
    """
    try:
        # Check if collection has data
        count = collection.count_documents({})
        
        if count == 0:
            print("Initializing database with sample users...")
            
            sample_users = [
                {
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'age': 28,
                    'country': 'USA',
                    'status': 'active',
                    'subscription': 'premium',
                    'email_verified': True,
                    'registered_at': datetime(2023, 1, 15)
                },
                {
                    'name': 'Jane Smith',
                    'email': 'jane@example.com',
                    'age': 34,
                    'country': 'Canada',
                    'status': 'active',
                    'subscription': 'basic',
                    'email_verified': True,
                    'registered_at': datetime(2023, 3, 20)
                },
                {
                    'name': 'Bob Johnson',
                    'email': 'bob@example.com',
                    'age': 45,
                    'country': 'UK',
                    'status': 'inactive',
                    'subscription': 'free',
                    'email_verified': False,
                    'registered_at': datetime(2022, 11, 5)
                },
                {
                    'name': 'Alice Brown',
                    'email': 'alice@example.com',
                    'age': 22,
                    'country': 'USA',
                    'status': 'active',
                    'subscription': 'free',
                    'email_verified': True,
                    'registered_at': datetime(2024, 1, 10)
                },
                {
                    'name': 'Charlie Wilson',
                    'email': 'charlie@example.com',
                    'age': 56,
                    'country': 'Australia',
                    'status': 'active',
                    'subscription': 'enterprise',
                    'email_verified': True,
                    'registered_at': datetime(2021, 6, 30)
                },
                {
                    'name': 'Diana Martinez',
                    'email': 'diana@example.com',
                    'age': 31,
                    'country': 'Germany',
                    'status': 'pending',
                    'subscription': 'basic',
                    'email_verified': False,
                    'registered_at': datetime(2024, 2, 14)
                },
                {
                    'name': 'Ethan Davis',
                    'email': 'ethan@example.com',
                    'age': 19,
                    'country': 'Canada',
                    'status': 'active',
                    'subscription': 'free',
                    'email_verified': True,
                    'registered_at': datetime(2024, 3, 1)
                },
                {
                    'name': 'Fiona Lee',
                    'email': 'fiona@example.com',
                    'age': 42,
                    'country': 'Japan',
                    'status': 'active',
                    'subscription': 'premium',
                    'email_verified': True,
                    'registered_at': datetime(2022, 8, 22)
                }
            ]
            
            collection.insert_many(sample_users)
            print(f"✓ Created {len(sample_users)} sample users\n")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")

def demonstrate_security():
    """
    Demonstrate why predefined filters are secure.
    """
    print("\n" + "="*70)
    print("SECURITY DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE APPROACH (NoSQL injection vulnerable):")
    print("-" * 70)
    print("If we allowed arbitrary user input like:")
    print('  user_input = {"$ne": null}')
    print("\nAnd built query like:")
    print('  query = {"email": user_input}')
    print("\nThis would become:")
    print('  {"email": {"$ne": null}}')
    print("\nThis matches ALL users (email not equal to null)!")
    print("An attacker could bypass authentication or extract all data.")
    
    print("\n✅ SECURE APPROACH (predefined filters):")
    print("-" * 70)
    print("Our system uses ONLY predefined query fragments:")
    print("  - User selects from menu options (1, 2, 3, etc.)")
    print("  - Each option maps to a PREDEFINED query")
    print("  - NO user input goes into the query")
    print("\nExample:")
    print('  User selects: "Age 26-35"')
    print('  System uses: {"age": {"$gte": 26, "$lte": 35}}')
    print("\nUser input NEVER becomes part of the query structure!")
    print("This completely prevents NoSQL injection attacks.")

def main():
    """Main function for secure MongoDB user filter"""
    print("="*70)
    print("        SECURE MONGODB USER FILTER")
    print("="*70)
    print("\nThis system demonstrates secure MongoDB queries using")
    print("predefined filter options to prevent NoSQL injection.")
    
    # Connect to database
    collection, client = connect_to_database()
    
    if not collection:
        print("\n✗ Cannot proceed without database connection")
        return
    
    try:
        # Initialize with sample data
        init_sample_database(collection)
        
        while True:
            print("\n" + "="*70)
            print("OPTIONS:")
            print("  1. Filter users")
            print("  2. Show all available filters")
            print("  3. Show security demonstration")
            print("  4. Show all users (no filters)")
            print("  5. Quit")
            print("="*70)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                # Select filters interactively
                selected_filters = select_filters()
                
                if not selected_filters:
                    print("\n⚠ No filters selected, showing all users")
                    query = {}
                else:
                    # Build query from validated selections
                    query = build_query(selected_filters)
                    print(f"\n✓ Built query: {query}")
                
                # Execute safe query
                users = execute_safe_query(collection, query)
                
                # Display results
                display_users(users, query)
            
            elif choice == '2':
                show_filter_menu()
            
            elif choice == '3':
                demonstrate_security()
            
            elif choice == '4':
                users = execute_safe_query(collection, {})
                display_users(users, {})
            
            elif choice == '5':
                print("\nGoodbye!")
                break
            
            else:
                print("✗ Invalid option")
    
    finally:
        if client:
            client.close()
            print("\n✓ Database connection closed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)