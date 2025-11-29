from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime, timedelta
import sys
import re

# Database configuration
MONGO_CONFIG = {
    'connection_string': 'mongodb://localhost:27017/',
    'database': 'blog_database',
    'collection': 'posts'
}

# SECURITY: Define allowed searchable fields
ALLOWED_SEARCH_FIELDS = {
    'author': {
        'description': 'Search by author name',
        'type': 'text',
        'validation': lambda x: len(x) >= 2 and len(x) <= 100
    },
    'tag': {
        'description': 'Search by tag',
        'type': 'text',
        'validation': lambda x: len(x) >= 2 and len(x) <= 50
    },
    'title': {
        'description': 'Search by title (case-insensitive)',
        'type': 'text',
        'validation': lambda x: len(x) >= 2 and len(x) <= 200
    },
    'status': {
        'description': 'Search by post status',
        'type': 'choice',
        'choices': ['draft', 'published', 'archived']
    },
    'category': {
        'description': 'Search by category',
        'type': 'choice',
        'choices': ['technology', 'business', 'lifestyle', 'tutorial', 'news']
    }
}

# SECURITY: Define allowed date range options
DATE_RANGE_OPTIONS = {
    '1': {'label': 'Last 7 days', 'days': 7},
    '2': {'label': 'Last 30 days', 'days': 30},
    '3': {'label': 'Last 90 days', 'days': 90},
    '4': {'label': 'Last year', 'days': 365},
    '5': {'label': 'All time', 'days': None}
}

# SECURITY: Define which fields to display in results
ALLOWED_OUTPUT_FIELDS = {
    '_id': False,  # Don't show MongoDB internal ID
    'title': True,
    'author': True,
    'created_at': True,
    'status': True,
    'category': True,
    'tags': True,
    'excerpt': True,
    'views': True
}

def connect_to_database():
    """
    Establish secure connection to MongoDB.
    
    Returns:
        Tuple of (collection, client) or (None, None)
    """
    try:
        client = MongoClient(
            MONGO_CONFIG['connection_string'],
            serverSelectionTimeoutMS=5000
        )
        
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

def validate_text_input(value, field_name):
    """
    Validate text input for a searchable field.
    
    Args:
        value: Input value to validate
        field_name: Name of the field being validated
    
    Returns:
        Tuple of (is_valid: bool, cleaned_value: str, error_message: str)
    """
    if not value or not value.strip():
        return False, None, f"{field_name} cannot be empty"
    
    cleaned = value.strip()
    
    # Get field configuration
    field_config = ALLOWED_SEARCH_FIELDS.get(field_name)
    if not field_config:
        return False, None, f"Invalid field: {field_name}"
    
    # Apply field-specific validation
    if 'validation' in field_config:
        if not field_config['validation'](cleaned):
            return False, None, f"{field_name} validation failed"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\$where',
        r'\$function',
        r'{\s*\$',
        r'function\s*\(',
        r'eval\s*\('
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False, None, f"{field_name} contains suspicious content"
    
    return True, cleaned, None

def validate_choice_input(value, field_name):
    """
    Validate choice input against allowed choices.
    
    Args:
        value: Input value to validate
        field_name: Name of the field being validated
    
    Returns:
        Tuple of (is_valid: bool, value: str, error_message: str)
    """
    field_config = ALLOWED_SEARCH_FIELDS.get(field_name)
    if not field_config or field_config['type'] != 'choice':
        return False, None, f"Invalid choice field: {field_name}"
    
    if value not in field_config['choices']:
        return False, None, f"Invalid choice. Must be one of: {', '.join(field_config['choices'])}"
    
    return True, value, None

def build_text_query(field_name, value, exact_match=False):
    """
    Build a safe MongoDB query for text fields.
    
    Args:
        field_name: Name of the field to search
        value: Search value
        exact_match: Whether to require exact match
    
    Returns:
        Query dictionary
    """
    if exact_match:
        # Exact match (case-insensitive)
        return {field_name: {'$regex': f'^{re.escape(value)}$', '$options': 'i'}}
    else:
        # Partial match (case-insensitive)
        return {field_name: {'$regex': re.escape(value), '$options': 'i'}}

def build_tag_query(tag_value):
    """
    Build a safe MongoDB query for tag array field.
    
    Args:
        tag_value: Tag to search for
    
    Returns:
        Query dictionary
    """
    # Search in array field (case-insensitive)
    return {'tags': {'$regex': re.escape(tag_value), '$options': 'i'}}

def build_date_query(date_option):
    """
    Build a safe MongoDB query for date range.
    
    Args:
        date_option: Predefined date option key
    
    Returns:
        Query dictionary or empty dict for "all time"
    """
    if date_option not in DATE_RANGE_OPTIONS:
        return {}
    
    days = DATE_RANGE_OPTIONS[date_option]['days']
    
    if days is None:
        return {}  # All time - no date filter
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    return {'created_at': {'$gte': cutoff_date}}

def build_search_query(search_criteria):
    """
    Build complete MongoDB query from validated search criteria.
    Uses only safe, predefined query patterns.
    
    Args:
        search_criteria: Dictionary of validated search criteria
    
    Returns:
        MongoDB query dictionary
    """
    query_parts = []
    
    # Process each search criterion
    for field, value in search_criteria.items():
        if field == 'date_range':
            date_query = build_date_query(value)
            if date_query:
                query_parts.append(date_query)
        
        elif field == 'tag':
            query_parts.append(build_tag_query(value))
        
        elif field in ['author', 'title']:
            query_parts.append(build_text_query(field, value, exact_match=False))
        
        elif field in ['status', 'category']:
            # Exact match for choice fields
            query_parts.append({field: value})
    
    # Combine all query parts with $and
    if not query_parts:
        return {}
    elif len(query_parts) == 1:
        return query_parts[0]
    else:
        return {'$and': query_parts}

def execute_safe_search(collection, query, limit=50):
    """
    Execute MongoDB search with safe projection and limits.
    
    Args:
        collection: MongoDB collection object
        query: Query dictionary
        limit: Maximum results to return
    
    Returns:
        List of blog post documents
    """
    try:
        # Execute query with projection to limit returned fields
        results = list(
            collection.find(query, ALLOWED_OUTPUT_FIELDS)
            .sort('created_at', -1)  # Most recent first
            .limit(limit)
        )
        
        return results
        
    except OperationFailure as e:
        print(f"✗ Query execution error: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []

def display_results(posts, query):
    """
    Display search results in a safe, formatted manner.
    
    Args:
        posts: List of blog post documents
        query: The query that was executed
    """
    if not posts:
        print("\n" + "="*70)
        print("NO POSTS FOUND")
        print("="*70)
        print("No blog posts match your search criteria")
        return
    
    print("\n" + "="*70)
    print(f"FOUND {len(posts)} POST(S)")
    print("="*70)
    print(f"Query: {query}")
    print("="*70)
    
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post.get('title', 'Untitled')}")
        print("-" * 70)
        
        # Author
        print(f"   Author: {post.get('author', 'Unknown')}")
        
        # Date
        created = post.get('created_at')
        if created:
            if isinstance(created, datetime):
                print(f"   Published: {created.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"   Published: {created}")
        
        # Status and Category
        status = post.get('status', 'unknown')
        category = post.get('category', 'uncategorized')
        print(f"   Status: {status.capitalize()} | Category: {category.capitalize()}")
        
        # Tags
        tags = post.get('tags', [])
        if tags:
            print(f"   Tags: {', '.join(tags)}")
        
        # Excerpt
        excerpt = post.get('excerpt', post.get('content', ''))
        if excerpt:
            if len(excerpt) > 150:
                excerpt = excerpt[:147] + "..."
            print(f"   Excerpt: {excerpt}")
        
        # Views
        views = post.get('views', 0)
        print(f"   Views: {views}")
    
    print("\n" + "="*70)

def show_search_options():
    """Display available search options."""
    print("\n" + "="*70)
    print("AVAILABLE SEARCH FIELDS")
    print("="*70)
    
    for field, config in ALLOWED_SEARCH_FIELDS.items():
        print(f"\n• {field.upper()}: {config['description']}")
        if config['type'] == 'choice':
            print(f"  Options: {', '.join(config['choices'])}")
    
    print("\n• DATE_RANGE: Filter by publication date")
    for key, option in DATE_RANGE_OPTIONS.items():
        print(f"  {key}) {option['label']}")
    
    print("="*70)

def interactive_search():
    """
    Interactive search interface with guided input.
    
    Returns:
        Dictionary of validated search criteria
    """
    search_criteria = {}
    
    print("\n" + "="*70)
    print("BLOG POST SEARCH")
    print("="*70)
    print("Enter search criteria (press Enter to skip any field)")
    
    # Author search
    author = input("\nAuthor name: ").strip()
    if author:
        is_valid, cleaned, error = validate_text_input(author, 'author')
        if is_valid:
            search_criteria['author'] = cleaned
            print(f"✓ Added author filter: {cleaned}")
        else:
            print(f"✗ {error}")
    
    # Title search
    title = input("\nTitle keywords: ").strip()
    if title:
        is_valid, cleaned, error = validate_text_input(title, 'title')
        if is_valid:
            search_criteria['title'] = cleaned
            print(f"✓ Added title filter: {cleaned}")
        else:
            print(f"✗ {error}")
    
    # Tag search
    tag = input("\nTag: ").strip()
    if tag:
        is_valid, cleaned, error = validate_text_input(tag, 'tag')
        if is_valid:
            search_criteria['tag'] = cleaned
            print(f"✓ Added tag filter: {cleaned}")
        else:
            print(f"✗ {error}")
    
    # Category choice
    print("\nCategory options:", ", ".join(ALLOWED_SEARCH_FIELDS['category']['choices']))
    category = input("Category: ").strip().lower()
    if category:
        is_valid, value, error = validate_choice_input(category, 'category')
        if is_valid:
            search_criteria['category'] = value
            print(f"✓ Added category filter: {value}")
        else:
            print(f"✗ {error}")
    
    # Status choice
    print("\nStatus options:", ", ".join(ALLOWED_SEARCH_FIELDS['status']['choices']))
    status = input("Status: ").strip().lower()
    if status:
        is_valid, value, error = validate_choice_input(status, 'status')
        if is_valid:
            search_criteria['status'] = value
            print(f"✓ Added status filter: {value}")
        else:
            print(f"✗ {error}")
    
    # Date range
    print("\nDate range options:")
    for key, option in DATE_RANGE_OPTIONS.items():
        print(f"  {key}) {option['label']}")
    
    date_choice = input("Select date range: ").strip()
    if date_choice and date_choice in DATE_RANGE_OPTIONS:
        search_criteria['date_range'] = date_choice
        print(f"✓ Added date filter: {DATE_RANGE_OPTIONS[date_choice]['label']}")
    
    return search_criteria

def init_sample_database(collection):
    """
    Initialize database with sample blog posts.
    
    Args:
        collection: MongoDB collection object
    """
    try:
        count = collection.count_documents({})
        
        if count == 0:
            print("Initializing database with sample blog posts...")
            
            sample_posts = [
                {
                    'title': 'Getting Started with Python',
                    'author': 'John Doe',
                    'content': 'Python is a versatile programming language...',
                    'excerpt': 'Learn the basics of Python programming',
                    'status': 'published',
                    'category': 'tutorial',
                    'tags': ['python', 'programming', 'beginner'],
                    'created_at': datetime.now() - timedelta(days=5),
                    'views': 1250
                },
                {
                    'title': 'Advanced MongoDB Queries',
                    'author': 'Jane Smith',
                    'content': 'MongoDB provides powerful query capabilities...',
                    'excerpt': 'Master advanced MongoDB query techniques',
                    'status': 'published',
                    'category': 'tutorial',
                    'tags': ['mongodb', 'database', 'nosql'],
                    'created_at': datetime.now() - timedelta(days=15),
                    'views': 890
                },
                {
                    'title': 'The Future of Technology',
                    'author': 'Alice Brown',
                    'content': 'Technology trends are evolving rapidly...',
                    'excerpt': 'Exploring upcoming technology trends',
                    'status': 'published',
                    'category': 'technology',
                    'tags': ['technology', 'trends', 'future'],
                    'created_at': datetime.now() - timedelta(days=2),
                    'views': 2100
                },
                {
                    'title': 'Business Strategy in 2024',
                    'author': 'Bob Wilson',
                    'content': 'Modern business requires new approaches...',
                    'excerpt': 'Strategic planning for modern businesses',
                    'status': 'draft',
                    'category': 'business',
                    'tags': ['business', 'strategy', 'planning'],
                    'created_at': datetime.now() - timedelta(days=1),
                    'views': 0
                },
                {
                    'title': 'Healthy Living Tips',
                    'author': 'Carol Green',
                    'content': 'Maintaining a healthy lifestyle is important...',
                    'excerpt': 'Simple tips for healthier living',
                    'status': 'published',
                    'category': 'lifestyle',
                    'tags': ['health', 'lifestyle', 'wellness'],
                    'created_at': datetime.now() - timedelta(days=45),
                    'views': 3400
                },
                {
                    'title': 'Python Best Practices',
                    'author': 'John Doe',
                    'content': 'Writing clean and efficient Python code...',
                    'excerpt': 'Best practices for Python development',
                    'status': 'published',
                    'category': 'tutorial',
                    'tags': ['python', 'best-practices', 'coding'],
                    'created_at': datetime.now() - timedelta(days=20),
                    'views': 1800
                }
            ]
            
            collection.insert_many(sample_posts)
            print(f"✓ Created {len(sample_posts)} sample blog posts\n")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")

def demonstrate_security():
    """Demonstrate security features."""
    print("\n" + "="*70)
    print("SECURITY DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE APPROACH (NoSQL injection vulnerable):")
    print("-" * 70)
    print("If we accepted raw JSON/dict input:")
    print('  user_input = \'{"$where": "function() { return true; }"}\'')
    print("  query = json.loads(user_input)")
    print("\nThis would execute arbitrary JavaScript in MongoDB!")
    print("An attacker could extract all data or cause denial of service.")
    
    print("\n✅ SECURE APPROACH (our implementation):")
    print("-" * 70)
    print("1. User selects from PREDEFINED search fields")
    print("2. Each field has specific validation rules")
    print("3. Queries built using safe patterns only:")
    print("   - Text fields: {'field': {'$regex': escaped_value}}")
    print("   - Choice fields: {'field': validated_choice}")
    print("   - Date ranges: {'created_at': {'$gte': calculated_date}}")
    print("\n4. User input is:")
    print("   - Escaped before use in regex")
    print("   - Validated against allowed choices")
    print("   - Never interpreted as code or structure")
    print("\n5. Results limited to safe output fields only")
    print("\nThis completely prevents NoSQL injection!")

def main():
    """Main function for secure blog search tool"""
    print("="*70)
    print("        SECURE MONGODB BLOG SEARCH TOOL")
    print("="*70)
    print("\nSearch blog posts safely using validated, structured inputs.")
    
    collection, client = connect_to_database()
    
    if not collection:
        print("\n✗ Cannot proceed without database connection")
        return
    
    try:
        init_sample_database(collection)
        
        while True:
            print("\n" + "="*70)
            print("OPTIONS:")
            print("  1. Search blog posts")
            print("  2. Show available search fields")
            print("  3. Show security demonstration")
            print("  4. Show all published posts")
            print("  5. Quit")
            print("="*70)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                # Interactive search
                search_criteria = interactive_search()
                
                if not search_criteria:
                    print("\n⚠ No search criteria provided")
                    continue
                
                # Build safe query
                query = build_search_query(search_criteria)
                print(f"\n✓ Built query: {query}")
                
                # Execute search
                posts = execute_safe_search(collection, query)
                
                # Display results
                display_results(posts, query)
            
            elif choice == '2':
                show_search_options()
            
            elif choice == '3':
                demonstrate_security()
            
            elif choice == '4':
                query = {'status': 'published'}
                posts = execute_safe_search(collection, query, limit=20)
                display_results(posts, query)
            
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