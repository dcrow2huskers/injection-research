import os
import sys
import re
from pathlib import Path

def validate_directory(dir_path):
    """
    Validate that the directory path is safe and exists.
    
    Args:
        dir_path: Path to validate
    
    Returns:
        Path object if valid, None otherwise
    """
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(dir_path).resolve()
        
        # Check if path exists
        if not path.exists():
            print(f"Error: Directory does not exist: {path}")
            return None
        
        # Check if it's actually a directory
        if not path.is_dir():
            print(f"Error: Path is not a directory: {path}")
            return None
        
        # Check if we have read permissions
        if not os.access(path, os.R_OK):
            print(f"Error: No read permission for directory: {path}")
            return None
        
        return path
        
    except Exception as e:
        print(f"Error validating directory: {e}")
        return None

def validate_search_term(search_term):
    """
    Validate the search term.
    
    Args:
        search_term: String to search for
    
    Returns:
        True if valid, False otherwise
    """
    if not search_term:
        print("Error: Search term cannot be empty")
        return False
    
    if len(search_term) > 1000:
        print("Error: Search term is too long (max 1000 characters)")
        return False
    
    return True

def is_text_file(file_path):
    """
    Check if a file is likely a text file by reading its first bytes.
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if likely text, False otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 512 bytes
            chunk = f.read(512)
            
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return False
            
            # Try to decode as UTF-8
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
                
    except Exception:
        return False

def search_in_file(file_path, search_term, case_sensitive=False):
    """
    Safely search for a term in a file without using shell commands.
    
    Args:
        file_path: Path object to the file
        search_term: String to search for
        case_sensitive: Whether search should be case-sensitive
    
    Returns:
        List of tuples (line_number, line_content) where term was found
    """
    matches = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                # Perform search based on case sensitivity
                if case_sensitive:
                    if search_term in line:
                        matches.append((line_num, line.rstrip()))
                else:
                    if search_term.lower() in line.lower():
                        matches.append((line_num, line.rstrip()))
                        
    except PermissionError:
        # Skip files we can't read
        pass
    except Exception as e:
        # Skip files that cause other errors
        pass
    
    return matches

def search_directory(directory, search_term, case_sensitive=False, 
                    file_pattern=None, max_depth=None):
    """
    Safely search for a term in all text files in a directory.
    Uses Path.rglob() which is safe and doesn't invoke shell.
    
    Args:
        directory: Path object to search in
        search_term: String to search for
        case_sensitive: Whether search should be case-sensitive
        file_pattern: Optional file pattern (e.g., "*.txt")
        max_depth: Maximum directory depth to search
    
    Returns:
        Dictionary mapping file paths to lists of matches
    """
    results = {}
    files_searched = 0
    files_with_matches = 0
    
    print(f"\nSearching for '{search_term}' in: {directory}")
    print("="*70)
    
    try:
        # Use rglob for recursive search or glob for single directory
        if max_depth == 0:
            pattern = file_pattern if file_pattern else "*"
            file_iterator = directory.glob(pattern)
        else:
            pattern = f"**/{file_pattern}" if file_pattern else "**/*"
            file_iterator = directory.rglob(pattern.lstrip("**/"))
        
        for file_path in file_iterator:
            # Skip if not a file
            if not file_path.is_file():
                continue
            
            # Check depth limit if specified
            if max_depth is not None:
                try:
                    relative = file_path.relative_to(directory)
                    if len(relative.parts) - 1 > max_depth:
                        continue
                except ValueError:
                    continue
            
            # Skip non-text files
            if not is_text_file(file_path):
                continue
            
            files_searched += 1
            
            # Search in the file
            matches = search_in_file(file_path, search_term, case_sensitive)
            
            if matches:
                results[file_path] = matches
                files_with_matches += 1
                
                # Print results immediately
                print(f"\n{file_path}")
                print("-"*70)
                for line_num, line_content in matches:
                    # Highlight the search term in the output
                    if case_sensitive:
                        highlighted = line_content.replace(
                            search_term, 
                            f">>>{search_term}<<<"
                        )
                    else:
                        # Case-insensitive highlighting
                        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
                        highlighted = pattern.sub(
                            lambda m: f">>>{m.group()}<<<", 
                            line_content
                        )
                    
                    print(f"  Line {line_num}: {highlighted}")
        
        print("\n" + "="*70)
        print(f"Search complete: {files_searched} files searched, "
              f"{files_with_matches} files with matches")
        
    except Exception as e:
        print(f"Error during search: {e}")
    
    return results

def main():
    """Main function to run the safe text search tool"""
    print("="*70)
    print("           SAFE FILE TEXT SEARCH TOOL")
    print("="*70)
    print("\nThis tool safely searches for text in files without using shell commands.")
    print("Type 'quit' at any prompt to exit")
    
    while True:
        print("\n" + "="*70)
        
        # Get search term
        search_term = input("\nEnter search term: ").strip()
        
        if search_term.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not validate_search_term(search_term):
            continue
        
        # Get directory path
        dir_input = input("Enter directory path to search: ").strip()
        
        if dir_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Use current directory if empty
        if not dir_input:
            dir_input = "."
            print(f"Using current directory: {os.getcwd()}")
        
        # Validate directory
        directory = validate_directory(dir_input)
        if directory is None:
            continue
        
        # Ask for search options
        print("\nSearch options:")
        case_sensitive = input("Case-sensitive search? (yes/no) [no]: ").strip().lower()
        case_sensitive = case_sensitive in ['yes', 'y']
        
        file_pattern = input("File pattern (e.g., *.txt, *.py) [all files]: ").strip()
        if not file_pattern:
            file_pattern = None
        
        max_depth_input = input("Max directory depth (0=current only, blank=unlimited): ").strip()
        max_depth = None
        if max_depth_input:
            try:
                max_depth = int(max_depth_input)
            except ValueError:
                print("Invalid depth, using unlimited")
        
        # Perform the search using safe methods
        results = search_directory(
            directory, 
            search_term, 
            case_sensitive=case_sensitive,
            file_pattern=file_pattern,
            max_depth=max_depth
        )
        
        if not results:
            print(f"\nNo matches found for '{search_term}'")
        
        # Ask if user wants to search again
        another = input("\nPerform another search? (yes/no): ").strip().lower()
        if another not in ['yes', 'y']:
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)