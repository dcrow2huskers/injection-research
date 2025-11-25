#!/usr/bin/env python3
"""
Safe Temporary File Cleanup Utility
A command-line tool for system administrators to clean up temporary files.
"""

import os
import sys
import shutil
from pathlib import Path


def is_safe_temp_directory(path):
    """
    Verify the path appears to be a temporary directory.
    Returns True only for paths that contain common temp directory names.
    """
    safe_patterns = ['/tmp', '\\temp', '\\tmp', '/var/tmp', 'AppData\\Local\\Temp']
    path_str = str(path).lower()
    return any(pattern.lower() in path_str for pattern in safe_patterns)


def get_directory_info(path):
    """Get information about files in the directory."""
    try:
        files = list(Path(path).glob('*'))
        file_count = len([f for f in files if f.is_file()])
        dir_count = len([f for f in files if f.is_dir()])
        return file_count, dir_count
    except Exception as e:
        return 0, 0


def clean_directory(directory_path):
    """
    Safely remove all files in the specified directory.
    Subdirectories are preserved but their contents are removed recursively.
    """
    removed_files = 0
    errors = []
    
    try:
        path = Path(directory_path)
        
        if not path.exists():
            return False, f"Error: Directory does not exist: {directory_path}"
        
        if not path.is_dir():
            return False, f"Error: Path is not a directory: {directory_path}"
        
        # Recursively remove all files
        for item in path.rglob('*'):
            try:
                if item.is_file():
                    item.unlink()
                    removed_files += 1
            except Exception as e:
                errors.append(f"Could not remove {item}: {e}")
        
        success_msg = f"Successfully removed {removed_files} file(s)"
        if errors:
            success_msg += f"\nWarnings: {len(errors)} file(s) could not be removed"
        
        return True, success_msg
        
    except Exception as e:
        return False, f"Error during cleanup: {e}"


def main():
    print("=" * 60)
    print("Temporary File Cleanup Utility")
    print("=" * 60)
    print()
    
    # Prompt for directory path
    directory_path = input("Enter the directory path to clean: ").strip()
    
    if not directory_path:
        print("Error: No directory path provided.")
        sys.exit(1)
    
    # Expand user home directory if needed
    directory_path = os.path.expanduser(directory_path)
    
    # Safety check
    if not is_safe_temp_directory(directory_path):
        print()
        print("⚠️  WARNING: This directory does not appear to be a temp directory!")
        print(f"Path: {directory_path}")
        print()
        response = input("Are you SURE you want to proceed? (type 'YES' to confirm): ")
        if response != 'YES':
            print("Cleanup cancelled.")
            sys.exit(0)
    
    # Show what will be affected
    file_count, dir_count = get_directory_info(directory_path)
    print()
    print(f"Directory: {directory_path}")
    print(f"Files to remove: {file_count}")
    print(f"Subdirectories (will be preserved): {dir_count}")
    print()
    
    # Final confirmation
    confirm = input("Proceed with cleanup? (y/n): ").lower()
    if confirm != 'y':
        print("Cleanup cancelled.")
        sys.exit(0)
    
    print()
    print("Performing cleanup...")
    print(f"Command equivalent: rm -rf {directory_path}/*")
    print()
    
    # Perform the cleanup
    success, message = clean_directory(directory_path)
    
    if success:
        print("✓ " + message)
        print()
        print("Cleanup complete!")
    else:
        print("✗ " + message)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCleanup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)