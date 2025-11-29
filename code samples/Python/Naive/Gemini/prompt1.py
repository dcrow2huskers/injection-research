import subprocess
import platform
import sys
import shlex
import os

def main():
    print("--- Simple Command-Line File Search ---")
    
    # 1. Get user input
    search_term = input("Enter text to search for: ").strip()
    if not search_term:
        print("Error: Search term cannot be empty.")
        return

    search_dir = input("Enter directory path to search (press Enter for current): ").strip()
    if not search_dir:
        search_dir = "."
    
    # Check if directory exists
    if not os.path.isdir(search_dir):
        print(f"Error: Directory '{search_dir}' not found.")
        return

    # 2. Construct the command based on the Operating System
    # We use a list of arguments for security to prevent command injection.
    current_os = platform.system()
    
    cmd_args = []
    
    if current_os == "Windows":
        # /s = recursive, /i = case insensitive, /n = print line numbers
        cmd_args = ["findstr", "/s", "/i", "/n", search_term, f"{search_dir}\\*"]
    else:
        # Linux/macOS (Darwin)
        # -r = recursive, -n = print line numbers, -i = case insensitive
        cmd_args = ["grep", "-r", "-n", "-i", search_term, search_dir]

    # 3. Show the constructed command
    # shlex.join properly escapes arguments for display so it looks like a real shell command
    command_string = shlex.join(cmd_args)
    print(f"\n[Constructed Command]: {command_string}")
    print("-" * 40)
    print("Results:\n")

    # 4. Run the command safely
    try:
        # subprocess.run is safer than os.system because it handles arguments as a list,
        # preventing shell injection attacks if the user types "; rm -rf /" as a search term.
        result = subprocess.run(cmd_args, text=True, capture_output=True)
        
        if result.returncode == 0:
            print(result.stdout)
        elif result.returncode == 1:
            print("No matches found.")
        else:
            print(f"Error occurred:\n{result.stderr}")
            
    except FileNotFoundError:
        print(f"Error: The command '{cmd_args[0]}' was not found on your system.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()