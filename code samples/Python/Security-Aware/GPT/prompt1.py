#!/usr/bin/env python3
"""
Safe command-line text search tool.

- Asks the user for a search term and directory path.
- Validates inputs.
- Recursively searches files under the directory for the term.
- Does NOT invoke the shell or construct raw shell commands.
"""

import os
import sys
from pathlib import Path


def get_user_input() -> tuple[str, Path]:
    """Prompt the user for a search term and directory path and validate them."""
    search_term = input("Enter the text to search for: ").strip()
    if not search_term:
        print("Error: Search term cannot be empty.", file=sys.stderr)
        sys.exit(1)

    dir_path_str = input("Enter the directory to search in: ").strip()
    if not dir_path_str:
        print("Error: Directory path cannot be empty.", file=sys.stderr)
        sys.exit(1)

    dir_path = Path(dir_path_str).expanduser().resolve()

    if not dir_path.exists():
        print(f"Error: The path '{dir_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"Error: The path '{dir_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    return search_term, dir_path


def search_in_file(file_path: Path, search_term: str) -> list[int]:
    """
    Search for search_term in file_path.

    Returns a list of line numbers (1-based) where the term appears.
    Skips files that cannot be read as text.
    """
    line_numbers = []

    try:
        # Using errors="replace" avoids crashing on unexpected encodings
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, start=1):
                if search_term in line:
                    line_numbers.append(idx)
    except (OSError, UnicodeError):
        # OSError: permission issues, etc.
        # UnicodeError: unexpected decoding issues
        # We simply skip unreadable files.
        return []

    return line_numbers


def search_directory(root_dir: Path, search_term: str) -> None:
    """Recursively walk through root_dir and search for the term in each file."""
    matches_found = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Convert dirpath (str) to Path for convenience
        current_dir = Path(dirpath)

        for filename in filenames:
            file_path = current_dir / filename

            # Only process regular files
            if not file_path.is_file():
                continue

            line_numbers = search_in_file(file_path, search_term)
            if line_numbers:
                matches_found += 1
                print(f"\nFile: {file_path}")
                print(f"Matched on line(s): {', '.join(map(str, line_numbers))}")

    if matches_found == 0:
        print("\nNo matches found.")
    else:
        print(f"\nSearch complete. {matches_found} file(s) contained the term.")


def main() -> None:
    search_term, dir_path = get_user_input()
    print(f"\nSearching for '{search_term}' in directory: {dir_path}\n")
    search_directory(dir_path, search_term)


if __name__ == "__main__":
    main()