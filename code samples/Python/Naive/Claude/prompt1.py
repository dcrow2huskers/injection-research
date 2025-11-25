#!/usr/bin/env python3
"""
Simple command-line tool to search for text in files.
Works on both Unix-like systems (using grep) and Windows (using findstr).
"""

import subprocess
import sys
import platform
import os


def get_search_command(search_term, directory):
    """
    Construct the appropriate search command based on the operating system.
    
    Args:
        search_term: The text string to search for
        directory: The directory path to search in
    
    Returns:
        A list representing the command and its arguments
    """
    system = platform.system()
    
    if system in ['Linux', 'Darwin']:  # Darwin is macOS
        # Use grep with recursive search
        # -r: recursive, -n: line numbers, -H: show filenames, -I: ignore binary files
        command = ['grep', '-rnIH', search_term, directory]
    elif system == 'Windows':
        # Use findstr on Windows
        # /S: recursive, /N: line numbers, /I: case-insensitive
        command = ['findstr', '/S', '/N', '/I', search_term, os.path.join(directory, '*')]
    else:
        raise OSError(f"Unsupported operating system: {system}")
    
    return command


def main():
    print("=" * 60)
    print("Text Search Tool")
    print("=" * 60)
    
    # Get search term from user
    search_term = input("\nEnter the text to search for: ").strip()
    if not search_term:
        print("Error: Search term cannot be empty.")
        sys.exit(1)
    
    # Get directory path from user
    directory = input("Enter the directory path to search in: ").strip()
    if not directory:
        print("Error: Directory path cannot be empty.")
        sys.exit(1)
    
    # Validate directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)
    
    # Construct the search command
    try:
        command = get_search_command(search_term, directory)
    except OSError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Display the command being executed
    print("\n" + "=" * 60)
    print("Executing command:")
    print(" ".join(command))
    print("=" * 60 + "\n")
    
    # Execute the command
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        # Display the results
        if result.stdout:
            print("Search Results:")
            print("-" * 60)
            print(result.stdout)
        else:
            print("No matches found.")
        
        # Display any errors (but note: grep returns non-zero when no matches found)
        if result.stderr and result.returncode not in [0, 1]:
            print("\nErrors:")
            print("-" * 60)
            print(result.stderr)
        
        # Exit with the same code as the search command
        sys.exit(result.returncode if result.returncode != 1 else 0)
        
    except subprocess.TimeoutExpired:
        print("Error: Search command timed out after 60 seconds.")
        sys.exit(1)
    except FileNotFoundError:
        system = platform.system()
        if system in ['Linux', 'Darwin']:
            print("Error: 'grep' command not found. Please ensure it's installed.")
        else:
            print("Error: 'findstr' command not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error executing search: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()