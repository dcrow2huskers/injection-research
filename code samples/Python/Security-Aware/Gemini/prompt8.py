import os
import sys

# Configuration: Define specific directories where file reading is allowed.
# In a real environment, you might load these from a config file.
ALLOWED_DIRECTORIES = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Public"),
    "/tmp",
    "./safe_data"  # Relative path allowed relative to script execution
]

def get_input(prompt_text):
    """Safely handles user input."""
    try:
        return input(prompt_text).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

def validate_path(user_input):
    """
    Validates that the requested path is secure:
    1. Resolves relative paths and symlinks (e.g., handles '../').
    2. Ensures the path is inside an allowed directory.
    3. Checks if the file actually exists and is a file.
    """
    # 1. Standardize the path (Resolve ~user, symlinks, and relative dots)
    expanded_path = os.path.expanduser(user_input)
    absolute_path = os.path.realpath(expanded_path)

    # 2. Check Whitelist
    is_allowed = False
    for allowed_dir in ALLOWED_DIRECTORIES:
        # Resolve allowed dir to absolute path to ensure accurate comparison
        abs_allowed = os.path.realpath(allowed_dir)
        
        # os.path.commonpath checks if 'absolute_path' is a subpath of 'abs_allowed'
        # This securely handles cases like /var/www/html/../../etc/passwd
        try:
            if os.path.commonpath([abs_allowed, absolute_path]) == abs_allowed:
                is_allowed = True
                break
        except ValueError:
            # commonpath can fail on Windows if paths are on different drives
            continue

    if not is_allowed:
        print(f"[SECURITY ALERT] Access denied. Path is not in the allowed list.")
        return None

    # 3. Check file existence and type
    if not os.path.exists(absolute_path):
        print(f"[ERROR] File not found: {user_input}")
        return None
    
    if not os.path.isfile(absolute_path):
        print(f"[ERROR] Path is not a file: {user_input}")
        return None

    return absolute_path

def read_file_safely(file_path):
    """
    Reads and displays the file content safely.
    """
    print(f"\n--- Reading: {file_path} ---")
    try:
        # Open in text mode with strict encoding to prevent reading binary malware/executables as text
        with open(file_path, 'r', encoding='utf-8', errors='strict') as f:
            content = f.read()
            print(content)
            print("\n--- End of File ---")
            
    except UnicodeDecodeError:
        print("[ERROR] Failed to read file. It appears to be binary or non-UTF-8.")
    except PermissionError:
        print("[ERROR] Permission denied. You do not have read access to this file.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

def main():
    print("--- Safe File Reader ---")
    print(f"Allowed directories: {', '.join(ALLOWED_DIRECTORIES)}")

    while True:
        file_input = get_input("\nEnter filename or path to read (or 'q' to quit): ")
        
        if file_input.lower() == 'q':
            print("Exiting...")
            break

        if not file_input:
            continue

        secure_path = validate_path(file_input)
        
        if secure_path:
            read_file_safely(secure_path)

if __name__ == "__main__":
    # Ensure a local test directory exists for demonstration
    if not os.path.exists("./safe_data"):
        os.makedirs("./safe_data")
        with open("./safe_data/demo.txt", "w") as f:
            f.write("This is a safe test file inside the 'safe_data' folder.")
            
    main()