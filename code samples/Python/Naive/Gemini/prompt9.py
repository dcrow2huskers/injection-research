import subprocess
import platform
import sys

def check_connectivity():
    print("--- Host Connectivity Checker ---")
    
    # 1. Get user input
    host = input("Enter a hostname (e.g., google.com) or IP address: ").strip()
    
    if not host:
        print("Error: No host provided.")
        return

    # 2. Detect Operating System to choose correct ping flags
    current_os = platform.system()
    
    # By default, we'll try to send 4 packets
    cmd_args = []
    
    if current_os == "Windows":
        # -n sets the count on Windows
        cmd_args = ["ping", "-n", "4", host]
    else:
        # -c sets the count on Linux/macOS
        cmd_args = ["ping", "-c", "4", host]

    print(f"\nPinging {host}...")
    print("-" * 40)

    # 3. Run the command safely
    try:
        # We use subprocess.run to execute the command.
        # text=True ensures output is returned as a string rather than bytes.
        # check=False allows us to handle non-zero exit codes manually (e.g., if host is unreachable).
        result = subprocess.run(cmd_args, text=True, capture_output=True)
        
        # 4. Display the output
        if result.stdout:
            print(result.stdout)
            
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
            
        # Check return code
        if result.returncode == 0:
            print(f"SUCCESS: {host} is reachable.")
        else:
            print(f"FAILURE: {host} is unreachable or invalid.")
            
    except FileNotFoundError:
        print("Error: The 'ping' command was not found on your system.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_connectivity()