import os

def read_and_print_file(file_path):
    """
    Attempt to read and print the contents of a file.
    
    Args:
        file_path: Path to the file to read
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"\nError: File not found at '{file_path}'")
            return False
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(file_path):
            print(f"\nError: '{file_path}' is not a file")
            return False
        
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"\nFile: {file_path}")
        print(f"Size: {file_size} bytes")
        print("="*70)
        
        # Try to read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
            print(contents)
        
        print("="*70)
        print(f"Successfully read {len(contents)} characters")
        return True
        
    except UnicodeDecodeError:
        print(f"\nError: Unable to read file as text. It may be a binary file.")
        
        # Offer to show hex dump for binary files
        response = input("Would you like to see a hex dump? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            try:
                with open(file_path, 'rb') as file:
                    binary_data = file.read(512)  # Read first 512 bytes
                    print("\nFirst 512 bytes (hex):")
                    print("="*70)
                    for i in range(0, len(binary_data), 16):
                        hex_part = ' '.join(f'{b:02x}' for b in binary_data[i:i+16])
                        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in binary_data[i:i+16])
                        print(f"{i:04x}  {hex_part:<48}  {ascii_part}")
                    print("="*70)
            except Exception as e:
                print(f"Error reading binary data: {e}")
        return False
        
    except PermissionError:
        print(f"\nError: Permission denied to read '{file_path}'")
        return False
        
    except IsADirectoryError:
        print(f"\nError: '{file_path}' is a directory, not a file")
        return False
        
    except Exception as e:
        print(f"\nError reading file: {e}")
        return False

def main():
    """Main function to run the file reader"""
    print("="*70)
    print("              FILE CONTENT READER")
    print("="*70)
    print("\nThis script will read and display the contents of any file.")
    print("Type 'quit' to exit")
    
    while True:
        print("\n" + "-"*70)
        
        # Prompt user for file path
        file_path = input("\nEnter filename or full file path: ").strip()
        
        # Check for exit command
        if file_path.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        # Check for empty input
        if not file_path:
            print("Please enter a valid file path")
            continue
        
        # Remove surrounding quotes if present (useful for paths with spaces)
        if (file_path.startswith('"') and file_path.endswith('"')) or \
           (file_path.startswith("'") and file_path.endswith("'")):
            file_path = file_path[1:-1]
        
        # Attempt to read and print the file
        read_and_print_file(file_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")