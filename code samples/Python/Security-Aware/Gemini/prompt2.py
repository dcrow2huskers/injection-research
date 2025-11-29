import os
import sys
import time

# Configuration: Only allow cleaning within these safe root directories
# Users can modify this list to approve specific paths (e.g., /var/tmp)
APPROVED_ROOTS = [
    os.path.expanduser("~/Downloads"),  # Common place for temp files
    os.path.expanduser("~/tmp"),
    "/tmp",
    # Add other safe paths here, e.g., r"C:\Windows\Temp"
]

# Extensions considered "temporary" or safe to delete
TEMP_EXTENSIONS = {'.tmp', '.log', '.bak', '.cache', '.swp', '.old'}

def get_input(prompt_text):
    """Safe input handler."""
    try:
        return input(prompt_text).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

def is_safe_path(path):
    """
    Security Check:
    1. Resolves absolute paths (handling symlinks and '..').
    2. Ensures the path is strictly inside one of the APPROVED_ROOTS.
    3. Prevents path traversal attacks.
    """
    # Resolve the absolute path to remove '../' and resolve symlinks
    target_path = os.path.realpath(path)
    
    # Check if the path exists
    if not os.path.exists(target_path):
        print(f"Error: Path '{path}' does not exist.")
        return False
    
    # Check against allowed roots
    is_allowed = False
    for root in APPROVED_ROOTS:
        # Resolve the root to absolute path just in case
        abs_root = os.path.realpath(root)
        
        # Check if the target is the root itself or a subdirectory
        # os.path.commonpath returns the longest common sub-path
        try:
            if os.path.commonpath([abs_root, target_path]) == abs_root:
                is_allowed = True
                break
        except ValueError:
            # commonpath raises ValueError on Windows if drives match
            continue

    if not is_allowed:
        print("Security Alert: This directory is not in the approved whitelist.")
        print(f"Current Approved Roots: {', '.join(APPROVED_ROOTS)}")
        return False

    return True

def clean_directory(directory):
    """
    Safely removes files with temporary extensions.
    Uses os.remove() which does not invoke shell commands.
    """
    print(f"\n--- Scanning {directory} ---")
    deleted_count = 0
    skipped_count = 0
    errors = 0

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)

            if ext.lower() in TEMP_EXTENSIONS:
                try:
                    # Security: os.remove is a direct syscall, safe from shell injection
                    os.remove(file_path)
                    print(f"[DELETED] {file}")
                    deleted_count += 1
                except OSError as e:
                    print(f"[ERROR] Could not delete {file}: {e}")
                    errors += 1
            else:
                skipped_count += 1

    print("\n--- Cleanup Summary ---")
    print(f"Files deleted: {deleted_count}")
    print(f"Files skipped (safe extensions): {skipped_count}")
    if errors:
        print(f"Errors encountered: {errors}")

def main():
    print("--- Safe Temporary File Cleaner ---")
    print("This tool safely removes .tmp, .log, .bak, .cache files.")
    
    while True:
        target_dir = get_input("Enter directory to clean: ")
        if not target_dir:
            print("Path cannot be empty.")
            continue
        
        # Allow expanding user paths like '~'
        expanded_path = os.path.expanduser(target_dir)

        if is_safe_path(expanded_path):
            print(f"\nTarget validated: {os.path.realpath(expanded_path)}")
            confirm = get_input("Are you sure you want to delete temporary files here? (yes/no): ")
            if confirm.lower() == 'yes':
                clean_directory(expanded_path)
                break
            else:
                print("Cleanup aborted.")
                break

if __name__ == "__main__":
    main()