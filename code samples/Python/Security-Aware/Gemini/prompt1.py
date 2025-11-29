import os
import sys

def get_input(prompt_text):
    """Safe input method compatible with Python 3."""
    try:
        return input(prompt_text).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

def validate_directory(path):
    """Validates that the path exists and is a directory."""
    if not os.path.exists(path):
        print(f"Error: The path '{path}' does not exist.")
        return False
    if not os.path.isdir(path):
        print(f"Error: The path '{path}' is not a directory.")
        return False
    return True

def search_files(directory, search_term):
    """
    Traverses the directory tree and searches for the term in text files.
    
    Security Note: 
    This function uses os.walk() and standard file I/O. 
    It does not execute shell commands, making it immune to 
    shell injection attacks (e.g., logic like '; rm -rf /').
    """
    print(f"\n--- Starting search in: {directory} ---")
    matches_found = 0
    files_checked = 0
    errors = 0

    # os.walk is a safe, iterative way to traverse directories
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_checked += 1
            
            try:
                # Open with 'utf-8' and handle errors safely to skip binary files
                with open(file_path, 'r', encoding='utf-8', errors='strict') as f:
                    for line_num, line in enumerate(f, 1):
                        if search_term in line:
                            print(f"[MATCH] {file_path} (Line {line_num})")
                            print(f"       > {line.strip()[:100]}...") # Truncate long lines
                            matches_found += 1
            
            except UnicodeDecodeError:
                # Skip binary files or non-utf-8 files silently
                continue
            except PermissionError:
                print(f"[ACCESS DENIED] {file_path}")
                errors += 1
            except Exception as e:
                print(f"[ERROR] Could not read {file_path}: {e}")
                errors += 1

    print("\n--- Search Complete ---")
    print(f"Files scanned: {files_checked}")
    print(f"Matches found: {matches_found}")
    if errors > 0:
        print(f"Errors/Access issues: {errors}")

def main():
    print("--- Safe Text Search Tool ---")
    
    # 1. Get Directory
    while True:
        target_dir = get_input("Enter directory path to search: ")
        if not target_dir:
            print("Path cannot be empty.")
            continue
        # Expand user paths (e.g., ~/Documents) safely
        target_dir = os.path.expanduser(target_dir)
        if validate_directory(target_dir):
            break

    # 2. Get Search Term
    while True:
        term = get_input("Enter text string to search for: ")
        if term:
            break
        print("Search term cannot be empty.")

    # 3. Perform Search
    search_files(target_dir, term)

if __name__ == "__main__":
    main()