import os
import sys
from pathlib import Path
import mimetypes

# SECURITY: Define allowed base directories
# Only files within these directories can be accessed
ALLOWED_BASE_DIRECTORIES = [
    './documents',      # Relative to current directory
    './data',
    './public',
    # Add more allowed directories as needed
    # Example: '/home/user/safe_folder'
]

# SECURITY: Define allowed file extensions (optional whitelist)
ALLOWED_EXTENSIONS = [
    '.txt', '.md', '.log', '.csv', '.json', '.xml',
    '.py', '.js', '.html', '.css', '.yaml', '.yml',
    '.conf', '.cfg', '.ini'
]

# Maximum file size to read (in bytes) - prevents memory exhaustion
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def initialize_safe_directories():
    """
    Create allowed directories if they don't exist.
    For demonstration purposes only.
    """
    for directory in ALLOWED_BASE_DIRECTORIES:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {dir_path.resolve()}")
            except Exception as e:
                print(f"⚠ Could not create directory {directory}: {e}")

def validate_file_path(file_path_str):
    """
    Validate that a file path is safe and within allowed directories.
    Prevents path traversal attacks.
    
    Args:
        file_path_str: User-provided file path string
    
    Returns:
        Tuple of (is_valid: bool, resolved_path: Path or None, error_message: str)
    """
    # Check for empty input
    if not file_path_str or not file_path_str.strip():
        return False, None, "File path cannot be empty"
    
    try:
        # Convert to Path object and resolve to absolute path
        # resolve() handles '..' and symlinks, preventing traversal
        user_path = Path(file_path_str).resolve()
        
        # Check if any allowed directory is a parent of the requested path
        is_allowed = False
        allowed_parent = None
        
        for allowed_dir in ALLOWED_BASE_DIRECTORIES:
            # Resolve the allowed directory to absolute path
            allowed_path = Path(allowed_dir).resolve()
            
            # Check if user_path is within allowed_path
            try:
                # relative_to will raise ValueError if not relative
                user_path.relative_to(allowed_path)
                is_allowed = True
                allowed_parent = allowed_path
                break
            except ValueError:
                # Not relative to this allowed directory, try next
                continue
        
        if not is_allowed:
            error_msg = f"Access denied: File must be within allowed directories\n"
            error_msg += "Allowed directories:\n"
            for allowed_dir in ALLOWED_BASE_DIRECTORIES:
                error_msg += f"  - {Path(allowed_dir).resolve()}\n"
            return False, None, error_msg
        
        # Check if file exists
        if not user_path.exists():
            return False, None, f"File not found: {user_path}"
        
        # Check if it's actually a file (not a directory)
        if not user_path.is_file():
            return False, None, f"Path is not a file: {user_path}"
        
        # Optional: Check file extension
        if ALLOWED_EXTENSIONS and user_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            return False, None, f"File type not allowed: {user_path.suffix}\nAllowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Check file size
        file_size = user_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            return False, None, f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)"
        
        # All checks passed
        return True, user_path, None
        
    except Exception as e:
        return False, None, f"Path validation error: {e}"

def is_binary_file(file_path):
    """
    Check if a file is binary (non-text).
    
    Args:
        file_path: Path object
    
    Returns:
        True if likely binary, False if likely text
    """
    try:
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('text/'):
                return False
            if mime_type in ['application/json', 'application/xml', 'application/javascript']:
                return False
        
        # Read first 512 bytes to check for binary content
        with open(file_path, 'rb') as f:
            chunk = f.read(512)
            
        # Check for null bytes (common in binary files)
        if b'\x00' in chunk:
            return True
        
        # Try to decode as UTF-8
        try:
            chunk.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True
            
    except Exception:
        return True

def safe_read_file(file_path):
    """
    Safely read file contents with proper error handling.
    
    Args:
        file_path: Validated Path object
    
    Returns:
        Tuple of (success: bool, content: str or None, error_message: str)
    """
    try:
        # Check if file is binary
        if is_binary_file(file_path):
            return False, None, "File appears to be binary. Use a binary file viewer instead."
        
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        return True, content, None
        
    except PermissionError:
        return False, None, f"Permission denied: Cannot read {file_path}"
    
    except UnicodeDecodeError:
        return False, None, "File encoding error: Cannot decode as text"
    
    except OSError as e:
        return False, None, f"OS error reading file: {e}"
    
    except Exception as e:
        return False, None, f"Unexpected error reading file: {e}"

def display_file_info(file_path):
    """
    Display information about the file.
    
    Args:
        file_path: Path object
    """
    try:
        stats = file_path.stat()
        
        print(f"\n{'='*70}")
        print("FILE INFORMATION")
        print('='*70)
        print(f"Path: {file_path}")
        print(f"Name: {file_path.name}")
        print(f"Size: {stats.st_size:,} bytes")
        print(f"Extension: {file_path.suffix}")
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            print(f"MIME Type: {mime_type}")
        
        print('='*70)
        
    except Exception as e:
        print(f"⚠ Could not retrieve file info: {e}")

def display_file_content(content, file_path):
    """
    Display file content with line numbers and formatting.
    
    Args:
        content: File content string
        file_path: Path object
    """
    print(f"\n{'='*70}")
    print(f"CONTENT: {file_path.name}")
    print('='*70)
    
    lines = content.splitlines()
    
    # Show line numbers for readability
    for i, line in enumerate(lines, 1):
        # Truncate very long lines
        if len(line) > 200:
            line = line[:197] + "..."
        print(f"{i:4d} | {line}")
    
    print('='*70)
    print(f"Total lines: {len(lines)}")
    print(f"Total characters: {len(content):,}")
    print('='*70)

def create_sample_files():
    """
    Create sample files for testing.
    """
    samples = [
        {
            'path': './documents/sample.txt',
            'content': 'This is a sample text file.\nIt has multiple lines.\nYou can read this safely!'
        },
        {
            'path': './documents/config.json',
            'content': '{\n  "app_name": "SecureReader",\n  "version": "1.0",\n  "debug": false\n}'
        },
        {
            'path': './data/log.txt',
            'content': '2024-11-29 10:00:00 INFO: Application started\n2024-11-29 10:01:00 INFO: Processing request\n2024-11-29 10:02:00 INFO: Request completed'
        }
    ]
    
    created = []
    for sample in samples:
        file_path = Path(sample['path'])
        if not file_path.exists():
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(sample['content'])
                created.append(str(file_path))
            except Exception as e:
                print(f"⚠ Could not create {sample['path']}: {e}")
    
    if created:
        print(f"\n✓ Created {len(created)} sample file(s):")
        for path in created:
            print(f"  - {path}")

def demonstrate_path_traversal():
    """
    Demonstrate path traversal attack prevention.
    """
    print("\n" + "="*70)
    print("PATH TRAVERSAL ATTACK PREVENTION DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE APPROACH (vulnerable):")
    print("-" * 70)
    print("If we directly used user input without validation:")
    print("  user_input = '../../../etc/passwd'")
    print("  with open(user_input, 'r') as f:  # DANGEROUS!")
    print("      content = f.read()")
    print("\nAn attacker could read ANY file on the system!")
    print("Examples of malicious inputs:")
    print("  - ../../../etc/passwd")
    print("  - ../../.ssh/id_rsa")
    print("  - ../../../../../Windows/System32/config/SAM")
    
    print("\n✅ SECURE APPROACH (our implementation):")
    print("-" * 70)
    print("Our security measures:")
    print("\n1. PATH RESOLUTION:")
    print("   - Use Path.resolve() to get absolute path")
    print("   - Automatically resolves '..' and symlinks")
    print("   - Cannot escape the resolved directory")
    
    print("\n2. DIRECTORY WHITELIST:")
    print("   - Only allow files within predefined directories")
    print("   - Use relative_to() to verify path is within allowed directory")
    print("   - Reject any path outside the whitelist")
    
    print("\n3. VALIDATION CHECKS:")
    print("   - File exists check")
    print("   - Is regular file (not directory or device)")
    print("   - File extension whitelist")
    print("   - File size limits")
    
    print("\n4. SAFE FILE OPERATIONS:")
    print("   - Use context managers (with statement)")
    print("   - Proper exception handling")
    print("   - Binary file detection")
    
    print("\nExample of attack prevention:")
    malicious_inputs = [
        "../../../etc/passwd",
        "../../.env",
        "./documents/../../sensitive.key"
    ]
    
    for malicious in malicious_inputs:
        print(f"\n  Input: {malicious}")
        is_valid, path, error = validate_file_path(malicious)
        if is_valid:
            print(f"    ✗ FAILED TO BLOCK!")
        else:
            print(f"    ✓ BLOCKED: {error.split(chr(10))[0]}")
    
    print("\n" + "="*70)

def list_allowed_files():
    """
    List all readable files in allowed directories.
    """
    print("\n" + "="*70)
    print("AVAILABLE FILES IN ALLOWED DIRECTORIES")
    print("="*70)
    
    found_files = []
    
    for allowed_dir in ALLOWED_BASE_DIRECTORIES:
        dir_path = Path(allowed_dir).resolve()
        
        if not dir_path.exists():
            continue
        
        print(f"\nDirectory: {dir_path}")
        print("-" * 70)
        
        try:
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        relative_path = file_path.relative_to(dir_path)
                        print(f"  {relative_path} ({size:,} bytes)")
                        found_files.append(str(file_path))
                    except Exception:
                        pass
        except Exception as e:
            print(f"  Error listing directory: {e}")
    
    if not found_files:
        print("\nNo files found in allowed directories")
    
    print("="*70)

def main():
    """Main function for secure file reader"""
    print("="*70)
    print("        SECURE FILE READER")
    print("="*70)
    print("\nSafely read files with path validation and security controls.")
    
    # Initialize allowed directories
    initialize_safe_directories()
    
    # Create sample files for testing
    create_sample_files()
    
    # Show allowed directories
    print("\n" + "="*70)
    print("ALLOWED DIRECTORIES:")
    print("="*70)
    for allowed_dir in ALLOWED_BASE_DIRECTORIES:
        resolved = Path(allowed_dir).resolve()
        exists = "✓" if resolved.exists() else "✗"
        print(f"  {exists} {resolved}")
    print("="*70)
    
    while True:
        print("\n" + "="*70)
        print("OPTIONS:")
        print("  1. Read a file")
        print("  2. List available files")
        print("  3. Show security demonstration")
        print("  4. Quit")
        print("="*70)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            print("\n" + "="*70)
            print("READ FILE")
            print("="*70)
            
            file_path_input = input("\nEnter file path: ").strip()
            
            if not file_path_input:
                print("✗ No file path provided")
                continue
            
            # Validate the file path
            print("\n✓ Validating file path...")
            is_valid, validated_path, error = validate_file_path(file_path_input)
            
            if not is_valid:
                print(f"\n✗ VALIDATION FAILED:")
                print(f"{error}")
                continue
            
            print(f"✓ Path validated: {validated_path}")
            
            # Display file information
            display_file_info(validated_path)
            
            # Read the file
            print("\n✓ Reading file...")
            success, content, error = safe_read_file(validated_path)
            
            if not success:
                print(f"\n✗ READ FAILED:")
                print(f"{error}")
                continue
            
            # Display the content
            display_file_content(content, validated_path)
        
        elif choice == '2':
            list_allowed_files()
        
        elif choice == '3':
            demonstrate_path_traversal()
        
        elif choice == '4':
            print("\nGoodbye!")
            break
        
        else:
            print("✗ Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)