import subprocess
import platform
import sys
import os

def main():
    print("--- System Temporary File Cleanup Utility ---")
    print("WARNING: This tool deletes files. Use with caution.")
    
    # 1. Get directory input
    target_dir = input("Enter the full path of the directory to clean: ").strip()
    
    # Basic validation
    if not target_dir:
        print("Error: No path provided.")
        return
        
    # Expand user paths (like ~ on Linux) and get absolute path for clarity
    target_dir = os.path.abspath(os.path.expanduser(target_dir))
    
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        return

    # 2. Safety Confirmation
    print(f"\nTARGET: {target_dir}")
    print("All files inside this directory will be permanently deleted.")
    confirm = input("Are you sure you want to proceed? (yes/no): ").lower()
    
    if confirm != "yes":
        print("Operation cancelled.")
        return

    # 3. Construct the command based on OS
    current_os = platform.system()
    command_str = ""
    
    # Note: We use shell=True here because we need wildcard expansion (like *) 
    # which is handled by the shell, not the command executable itself.
    if current_os == "Windows":
        # /Q = Quiet mode (no confirmation), /F = Force delete read-only files, /S = Recursive
        # We quote the path to handle spaces safely
        command_str = f'del /Q /F /S "{target_dir}\\*"'
    else:
        # Linux/macOS
        # rm -rf = recursive force remove
        # We quote the path to handle spaces safely
        command_str = f'rm -rf "{target_dir}"/*'

    # 4. Show and Run the command
    print(f"\n[Executing Command]: {command_str}")
    print("-" * 40)

    try:
        # shell=True is required here to process the wildcard (*) correctly
        result = subprocess.run(command_str, shell=True, text=True, capture_output=True)
        
        if result.returncode == 0:
            print("Cleanup complete.")
            # On Windows, del might output details; on Linux rm is silent on success.
            if result.stdout.strip():
                print(result.stdout)
        else:
            print("Error occurred:")
            print(result.stderr)
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()