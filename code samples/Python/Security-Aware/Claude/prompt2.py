import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import stat

# SECURITY: Define allowed base directories for cleanup
# Only directories in this list (or their subdirectories) can be cleaned
ALLOWED_BASE_DIRECTORIES = [
    '/tmp',
    '/var/tmp',
    'C:\\Windows\\Temp',
    'C:\\Temp',
    '/var/cache',
]

# Add user-specific temp directories
if sys.platform == 'win32':
    user_temp = os.environ.get('TEMP')
    if user_temp:
        ALLOWED_BASE_DIRECTORIES.append(user_temp)
else:
    user_temp = f'/tmp/{os.environ.get("USER", "")}'
    if user_temp:
        ALLOWED_BASE_DIRECTORIES.append(user_temp)

# File patterns to consider as temporary files
TEMP_FILE_PATTERNS = [
    '*.tmp',
    '*.temp',
    '*.cache',
    '*.log',
    '*.bak',
    '*.old',
    '~*',
]

def is_path_allowed(target_path):
    """
    Validate that a path is within allowed directories.
    Prevents path traversal attacks.
    
    Args:
        target_path: Path to validate
    
    Returns:
        Tuple of (is_allowed: bool, resolved_path: Path or None)
    """
    try:
        # Resolve to absolute path (handles '..' and symlinks)
        resolved = Path(target_path).resolve()
        
        # Check if path exists
        if not resolved.exists():
            print(f"Error: Path does not exist: {resolved}")
            return False, None
        
        # Check if it's a directory
        if not resolved.is_dir():
            print(f"Error: Path is not a directory: {resolved}")
            return False, None
        
        # Check against allowed base directories
        for allowed_base in ALLOWED_BASE_DIRECTORIES:
            allowed_path = Path(allowed_base).resolve()
            
            # Check if target is the allowed path or a subdirectory
            try:
                resolved.relative_to(allowed_path)
                return True, resolved
            except ValueError:
                # Not relative to this allowed path, try next
                continue
        
        # Path is not within any allowed directory
        print(f"Error: Path is not in an allowed directory")
        print(f"Allowed directories:")
        for allowed in ALLOWED_BASE_DIRECTORIES:
            print(f"  - {allowed}")
        return False, None
        
    except Exception as e:
        print(f"Error validating path: {e}")
        return False, None

def is_safe_to_delete(file_path, min_age_days=0):
    """
    Check if a file is safe to delete based on various criteria.
    
    Args:
        file_path: Path to the file
        min_age_days: Minimum age in days before file can be deleted
    
    Returns:
        True if safe to delete, False otherwise
    """
    try:
        # Check if file is a regular file (not device, socket, etc.)
        if not file_path.is_file():
            return False
        
        # Skip if file is being used (try to detect locks)
        try:
            # Try to open file exclusively (only works on some systems)
            with open(file_path, 'rb') as f:
                pass
        except (PermissionError, OSError):
            # File might be in use, skip it
            return False
        
        # Check file age if minimum age is specified
        if min_age_days > 0:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - file_mtime
            if age < timedelta(days=min_age_days):
                return False
        
        # Don't delete system files or hidden important files
        filename = file_path.name.lower()
        if filename in ['.gitkeep', '.htaccess', '.env', 'desktop.ini', 'thumbs.db']:
            return False
        
        return True
        
    except Exception:
        return False

def get_directory_size(directory):
    """
    Calculate total size of all files in directory.
    
    Args:
        directory: Path to directory
    
    Returns:
        Total size in bytes
    """
    total_size = 0
    try:
        for item in directory.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (PermissionError, OSError):
                    pass
    except Exception:
        pass
    return total_size

def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def scan_directory(directory, min_age_days=0, file_patterns=None, dry_run=True):
    """
    Scan directory for temporary files to clean.
    
    Args:
        directory: Path object to scan
        min_age_days: Minimum file age in days
        file_patterns: List of patterns to match (or None for all)
        dry_run: If True, only show what would be deleted
    
    Returns:
        Tuple of (files_found, total_size)
    """
    files_to_delete = []
    total_size = 0
    
    print(f"\nScanning: {directory}")
    print("="*70)
    
    try:
        # Iterate through all files
        if file_patterns:
            # Use specific patterns
            for pattern in file_patterns:
                for file_path in directory.rglob(pattern):
                    if file_path.is_file() and is_safe_to_delete(file_path, min_age_days):
                        try:
                            size = file_path.stat().st_size
                            files_to_delete.append((file_path, size))
                            total_size += size
                        except (PermissionError, OSError):
                            pass
        else:
            # Scan all files
            for file_path in directory.rglob('*'):
                if file_path.is_file() and is_safe_to_delete(file_path, min_age_days):
                    try:
                        size = file_path.stat().st_size
                        files_to_delete.append((file_path, size))
                        total_size += size
                    except (PermissionError, OSError):
                        pass
        
        # Display results
        if files_to_delete:
            print(f"\nFound {len(files_to_delete)} file(s) to delete:")
            print(f"Total space to free: {format_size(total_size)}\n")
            
            # Show first 20 files
            for file_path, size in files_to_delete[:20]:
                relative_path = file_path.relative_to(directory)
                print(f"  {relative_path} ({format_size(size)})")
            
            if len(files_to_delete) > 20:
                print(f"  ... and {len(files_to_delete) - 20} more files")
        else:
            print("\nNo files found to delete")
        
        return files_to_delete, total_size
        
    except Exception as e:
        print(f"Error scanning directory: {e}")
        return [], 0

def delete_files(files_list, directory):
    """
    Safely delete files using filesystem APIs.
    
    Args:
        files_list: List of tuples (file_path, size)
        directory: Base directory for relative path display
    
    Returns:
        Tuple of (success_count, failed_count, bytes_deleted)
    """
    success_count = 0
    failed_count = 0
    bytes_deleted = 0
    
    print("\nDeleting files...")
    print("="*70)
    
    for file_path, size in files_list:
        try:
            # Use Path.unlink() instead of os.remove() - safer API
            file_path.unlink()
            
            relative_path = file_path.relative_to(directory)
            print(f"✓ Deleted: {relative_path}")
            
            success_count += 1
            bytes_deleted += size
            
        except PermissionError:
            relative_path = file_path.relative_to(directory)
            print(f"✗ Permission denied: {relative_path}")
            failed_count += 1
            
        except FileNotFoundError:
            # File already deleted or moved
            success_count += 1
            bytes_deleted += size
            
        except Exception as e:
            relative_path = file_path.relative_to(directory)
            print(f"✗ Error deleting {relative_path}: {e}")
            failed_count += 1
    
    print("\n" + "="*70)
    print(f"Successfully deleted: {success_count} files")
    print(f"Failed to delete: {failed_count} files")
    print(f"Total space freed: {format_size(bytes_deleted)}")
    
    return success_count, failed_count, bytes_deleted

def main():
    """Main function for the secure temp file cleaner"""
    print("="*70)
    print("        SECURE TEMPORARY FILE CLEANER")
    print("="*70)
    print("\nThis utility safely cleans temporary files from approved directories.")
    print("\nSecurity features:")
    print("  - Path validation prevents directory traversal")
    print("  - Only allowed directories can be cleaned")
    print("  - No shell commands are executed")
    print("  - Dry-run mode to preview before deletion")
    
    # Show allowed directories
    print(f"\nAllowed directories for cleanup:")
    for allowed_dir in ALLOWED_BASE_DIRECTORIES:
        if Path(allowed_dir).exists():
            print(f"  ✓ {allowed_dir}")
        else:
            print(f"  ✗ {allowed_dir} (does not exist)")
    
    while True:
        print("\n" + "="*70)
        
        # Get directory path from user
        dir_input = input("\nEnter directory path to clean (or 'quit' to exit): ").strip()
        
        if dir_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not dir_input:
            print("Please enter a directory path")
            continue
        
        # Validate the path
        is_allowed, validated_path = is_path_allowed(dir_input)
        
        if not is_allowed:
            continue
        
        print(f"\n✓ Path validated: {validated_path}")
        
        # Get cleanup options
        print("\nCleanup options:")
        
        # Minimum age
        age_input = input("Minimum file age in days [0 = all files]: ").strip()
        min_age = 0
        if age_input:
            try:
                min_age = int(age_input)
            except ValueError:
                print("Invalid age, using 0")
        
        # File patterns
        use_patterns = input("Use temp file patterns (*.tmp, *.cache, etc.)? (yes/no) [yes]: ").strip().lower()
        if use_patterns in ['no', 'n']:
            patterns = None
        else:
            patterns = TEMP_FILE_PATTERNS
        
        # Scan the directory (dry run first)
        files_list, total_size = scan_directory(
            validated_path,
            min_age_days=min_age,
            file_patterns=patterns,
            dry_run=True
        )
        
        if not files_list:
            continue
        
        # Confirm deletion
        print("\n" + "="*70)
        confirm = input(f"\nDelete these {len(files_list)} files? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            # Perform actual deletion
            delete_files(files_list, validated_path)
        else:
            print("Deletion cancelled")
        
        # Ask if user wants to continue
        another = input("\nClean another directory? (yes/no): ").strip().lower()
        if another not in ['yes', 'y']:
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        # Check if running with appropriate permissions
        if os.name != 'nt' and os.geteuid() == 0:
            print("\nWARNING: Running as root. This is not recommended.")
            proceed = input("Continue anyway? (yes/no): ").strip().lower()
            if proceed not in ['yes', 'y']:
                sys.exit(0)
        
        main()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)