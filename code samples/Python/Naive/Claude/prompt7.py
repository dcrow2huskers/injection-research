from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import json
import ast

def connect_to_database():
    """Establish connection to MongoDB blog database"""
    try:
        # Update with your MongoDB connection string
        client = MongoClient(
            'mongodb://localhost:27017/',
            serverSelectionTimeoutMS=5000
        )
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB blog database\n")
        
        # Access database and collection
        db = client['blog_database']
        collection = db['posts']
        
        return collection
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_filter(filter_str):
    """
    Parse user input into a MongoDB query filter.
    Accepts JSON or Python dictionary format.
    """
    filter_str = filter_str.strip()
    
    try:
        # First try parsing as JSON
        filter_dict = json.loads(filter_str)
        return filter_dict
    except json.JSONDecodeError:
        # Try parsing as Python dictionary using ast.literal_eval
        try:
            filter_dict = ast.literal_eval(filter_str)
            if isinstance(filter_dict, dict):
                return filter_dict
            else:
                print("Filter must be a dictionary/object")
                return None
        except (ValueError, SyntaxError) as e:
            print(f"Invalid filter format: {e}")
            return None

def search_posts(collection, query_filter):
    """Search for blog posts matching the filter"""
    try:
        # Find matching posts
        results = list(collection.find(query_filter))
        
        if results:
            print(f"\nFound {len(results)} post(s) matching the filter:\n")
            print("="*70)
            
            for i, post in enumerate(results, 1):
                title = post.get('title', 'Untitled')
                author = post.get('author', 'Unknown')
                tags = post.get('tags', [])
                created = post.get('created_at', 'N/A')
                
                print(f"\n{i}. {title}")
                print(f"   Author: {author}")
                if tags:
                    print(f"   Tags: {', '.join(tags)}")
                print(f"   Created: {created}")
                
                # Show excerpt if available
                content = post.get('content', '')
                if content:
                    excerpt = content[:100] + '...' if len(content) > 100 else content
                    print(f"   Excerpt: {excerpt}")
                
                print("-"*70)
        else:
            print("\nNo posts found matching the filter")
        
        return len(results)
        
    except OperationFailure as e:
        print(f"Error executing query: {e}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0

def show_examples():
    """Display example filter queries"""
    print("\n" + "="*70)
    print("EXAMPLE FILTERS:")
    print("="*70)
    print("\n1. Search by author:")
    print('   {"author": "John Doe"}')
    print("   or")
    print("   {'author': 'John Doe'}")
    
    print("\n2. Search by tag:")
    print('   {"tags": "python"}')
    
    print("\n3. Search by multiple tags (contains any):")
    print('   {"tags": {"$in": ["python", "mongodb"]}}')
    
    print("\n4. Search by author AND tag:")
    print('   {"author": "Jane Smith", "tags": "tutorial"}')
    
    print("\n5. Search posts with status published:")
    print('   {"status": "published"}')
    
    print("\n6. Complex query - author and multiple tags:")
    print('   {"author": "John Doe", "tags": {"$all": ["python", "database"]}}')
    
    print("\n7. Search by date range (posts after a date):")
    print('   {"created_at": {"$gte": "2024-01-01"}}')
    
    print("\n8. Text search in title:")
    print('   {"title": {"$regex": "MongoDB", "$options": "i"}}')
    
    print("\nMongoDB operators you can use:")
    print("  $eq, $ne, $gt, $gte, $lt, $lte - comparison")
    print("  $in, $nin - match any/none in array")
    print("  $all - match all elements in array")
    print("  $regex - pattern matching")
    print("="*70)

def show_collection_stats(collection):
    """Show basic statistics about the posts collection"""
    try:
        total = collection.count_documents({})
        print(f"\nTotal posts in database: {total}")
        
        # Get sample fields from first document
        sample = collection.find_one()
        if sample:
            print("\nAvailable fields in posts:")
            for key in sample.keys():
                if key != '_id':
                    print(f"  - {key}")
    except Exception as e:
        print(f"Could not retrieve collection stats: {e}")

def main():
    """Main function to run the blog post search tool"""
    collection = connect_to_database()
    
    if collection is None:
        print("Failed to connect to database. Exiting...")
        return
    
    print("="*70)
    print("        MONGODB BLOG POST SEARCH TOOL")
    print("="*70)
    
    show_collection_stats(collection)
    
    print("\nType 'help' to see example filters")
    print("Type 'stats' to see collection statistics")
    print("Type 'quit' to exit")
    
    try:
        while True:
            print("\n" + "="*70)
            filter_input = input("\nEnter filter expression (JSON/dict format): ").strip()
            
            if filter_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            if filter_input.lower() == 'help':
                show_examples()
                continue
            
            if filter_input.lower() == 'stats':
                show_collection_stats(collection)
                continue
            
            if not filter_input:
                print("Please enter a valid filter expression")
                continue
            
            # Parse the filter
            query_filter = parse_filter(filter_input)
            
            if query_filter is None:
                print("\nTip: Use JSON format like {\"author\": \"John\"}")
                print("     or Python dict format like {'author': 'John'}")
                continue
            
            print(f"\nExecuting MongoDB query:")
            print(json.dumps(query_filter, indent=2))
            
            # Execute search
            search_posts(collection, query_filter)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()