import os

def read_file_contents():
    print("--- Simple File Reader ---")
    
    # 1. Get user input
    # We strip whitespace but otherwise accept the path exactly as typed.
    file_path = input("Enter the filename or full file path to open: ").strip()
    
    if not file_path:
        print("Error: No path provided.")
        return

    print(f"\nAttempting to read: {file_path}")
    print("-" * 40)

    try:
        # 2. Open and read the file
        # 'r' mode opens for reading. encoding='utf-8' handles standard text files.
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 3. Print contents
            if content:
                print(content)
            else:
                print("[The file is empty]")
                
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied. You do not have read access to '{file_path}'.")
    except UnicodeDecodeError:
        print("Error: Unable to decode text. This might be a binary file (like an image) or use a different encoding.")
    except OSError as e:
        print(f"System Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    read_file_contents()