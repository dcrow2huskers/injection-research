#!/usr/bin/env python3
"""
Safe file reader.

- Asks the user for a filename or file path.
- Validates the path and restricts access to allowed directories.
- Prevents path traversal using realpath/abspath checks.
- Uses safe file handling and clear error messages.
"""

import os
import sys
from typing import List


# ---- Configuration: edit this list for your environment ----
# Only files inside these directories (or their subdirectories) will be readable.
ALLOWED_BASE_DIRS: List[str] = [
    os.path.expanduser("~/safe_files"),  # example directory
    os.path.abspath(os.getcwd()),        # current working directory
]


def normalize_allowed_dirs(dirs: List[str]) -> List[str]:
    """Return a list of canonical absolute directory paths."""
    normed = []
    for d in dirs:
        if not d:
            continue
        # realpath resolves symlinks, abspath normalizes
        normed.append(os.path.realpath(os.path.abspath(d)))
    return normed


def is_within_allowed_dirs(path: str, allowed_dirs: List[str]) -> bool:
    """
    Check whether 'path' is inside one of the allowed directories.
    Uses realpath to prevent path traversal via symlinks.
    """
    real = os.path.realpath(os.path.abspath(path))

    # On Windows, case-insensitive comparison is safer
    if os.name == "nt":
        real_cmp = os.path.normcase(real)
        for base in allowed_dirs:
            base_cmp = os.path.normcase(base)
            # allow the base dir itself and anything under it
            if real_cmp == base_cmp or real_cmp.startswith(base_cmp + os.sep):
                return True
    else:
        for base in allowed_dirs:
            if real == base or real.startswith(base + os.sep):
                return True

    return False


def prompt_non_empty(prompt_text: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def main():
    allowed_dirs = normalize_allowed_dirs(ALLOWED_BASE_DIRS)

    if not allowed_dirs:
        print("Configuration error: no allowed directories are configured.", file=sys.stderr)
        sys.exit(1)

    print("=== Safe File Reader ===")
    print("You may read files only from these directories (and their subdirectories):")
    for d in allowed_dirs:
        print(f"  - {d}")
    print()

    user_input = prompt_non_empty("Enter a filename or full file path: ")

    # Convert user path to absolute path relative to current directory if needed
    # If the user provided a relative path, it will be resolved against cwd.
    candidate_path = os.path.abspath(user_input)

    # Check that the path is within allowed directories
    if not is_within_allowed_dirs(candidate_path, allowed_dirs):
        print(
            "Error: Access to this path is not allowed. "
            "Please choose a file inside one of the allowed directories."
        )
        sys.exit(1)

    # Check that it exists and is a regular file
    if not os.path.exists(candidate_path):
        print("Error: The specified file does not exist.")
        sys.exit(1)

    if not os.path.isfile(candidate_path):
        print("Error: The specified path is not a regular file.")
        sys.exit(1)

    # Optional: check read permission
    if not os.access(candidate_path, os.R_OK):
        print("Error: You do not have permission to read this file.")
        sys.exit(1)

    # Safely open and read the file
    try:
        with open(candidate_path, "r", encoding="utf-8", errors="replace") as f:
            print("\n=== File Contents ===\n")
            for line in f:
                # Print exactly as-is; 'end' avoids double newlines
                print(line, end="")
    except OSError as e:
        print(f"Error: Unable to access the file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()