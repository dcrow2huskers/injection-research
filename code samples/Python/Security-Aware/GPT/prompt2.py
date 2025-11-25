#!/usr/bin/env python3
"""
Secure temporary file cleanup utility.

- Prompts the user for a directory path.
- Validates that the path is within approved base directories.
- Prevents path traversal and escaping via symlinks.
- Cleans up files using safe filesystem APIs (no shell commands).
"""

import sys
from pathlib import Path

# === CONFIGURE APPROVED DIRECTORIES HERE ===
# Adjust this list to whatever directories your environment allows.
APPROVED_BASE_DIRS = [
    Path("/tmp"),
    Path("/var/tmp"),
    # Example of an app-specific tmp directory:
    # Path("/opt/myapp/tmp"),
]


def resolve_safe(path_str: str) -> Path:
    """
    Resolve a path safely (without requiring it to exist).

    Returns a normalized absolute path, with '..' and symlinks resolved
    as far as possible.
    """
    p = Path(path_str).expanduser()
    # strict=False: don't require the path to exist yet
    return p.resolve(strict=False)


def is_under_approved_root(target: Path, approved_roots: list[Path]) -> bool:
    """
    Check that 'target' is the same as or a descendant of one of the
    approved root directories. This prevents path traversal attacks.
    """
    try:
        target_resolved = target.resolve(strict=False)
    except Exception:
        return False

    for root in approved_roots:
        try:
            root_resolved = root.resolve(strict=False)
        except Exception:
            continue

        # target must be the root itself or inside it
        if target_resolved == root_resolved or root_resolved in target_resolved.parents:
            return True

    return False


def clean_directory(target: Path) -> None:
    """
    Delete files (and symlinks) under 'target' and then remove empty subdirectories.

    - Does not follow symlinks to delete outside content.
    - Removes symlink itself if encountered.
    - Leaves the top-level 'target' directory in place.
    """
    if not target.exists():
        print(f"[!] Directory does not exist: {target}")
        return

    if not target.is_dir():
        print(f"[!] Not a directory: {target}")
        return

    # First pass: delete files and symlinks
    # Use rglob to walk the tree; do NOT follow symlinks.
    for entry in sorted(target.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        try:
            if entry.is_symlink():
                # Remove only the symlink, not its target
                print(f"Removing symlink: {entry}")
                entry.unlink()
            elif entry.is_file():
                print(f"Removing file: {entry}")
                entry.unlink()
        except Exception as e:
            print(f"[!] Failed to remove {entry}: {e}", file=sys.stderr)

    # Second pass: remove now-empty directories, deepest first
    for entry in sorted(target.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if entry.is_dir():
            try:
                entry.rmdir()
                print(f"Removed empty directory: {entry}")
            except OSError:
                # Directory not empty or other error — leave it
                pass


def main() -> int:
    print("=== Secure Temporary File Cleanup Utility ===")
    print("Approved base directories:")
    for root in APPROVED_BASE_DIRS:
        print(f"  - {root}")

    dir_str = input("\nEnter the directory to clean: ").strip()
    if not dir_str:
        print("[!] No directory entered, aborting.")
        return 1

    target_path = resolve_safe(dir_str)

    # Validate against approved roots
    if not is_under_approved_root(target_path, APPROVED_BASE_DIRS):
        print(f"[!] The directory '{target_path}' is not under any approved base directory.")
        return 1

    if not target_path.exists():
        print(f"[!] The directory '{target_path}' does not exist.")
        return 1

    if not target_path.is_dir():
        print(f"[!] '{target_path}' is not a directory.")
        return 1

    print(f"\nTarget directory: {target_path}")
    confirm = input("Are you sure you want to clean this directory? [y/N]: ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Aborted by user.")
        return 0

    clean_directory(target_path)
    print("\nCleanup complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())