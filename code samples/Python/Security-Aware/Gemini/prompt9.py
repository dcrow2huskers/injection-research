import subprocess
import platform
import re
import sys

def get_input(prompt_text):
    """Safely handles user input."""
    try:
        return input(prompt_text).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

def validate_host_format(host_input):
    """
    Validates that the input contains only safe characters for a hostname or IP.
    
    Security:
    - Uses a whitelist approach (only alphanumeric, dots, hyphens, and colons).
    - strictly rejects shell metacharacters like ';', '&', '|', '$', '`', etc.
    """
    if not host_input:
        return False
        
    # Regex explanation:
    # ^             : Start of string
    # [a-zA-Z0-9    : Alphanumeric characters
    #  .            : Dots (for IP/domains)
    #  -            : Hyphens (for domains)
    #  :            : Colons (for IPv6)
    # ]+            : One or more of these characters
    # $             : End of string
    pattern = r"^[a-zA-Z0-9.:-]+$"
    
    if re.match(pattern, host_input):
        return True
    return False

def check_reachability(host):
    """
    Executes the ping command securely using subprocess.
    """
    # 1. Determine the correct ping flag based on OS
    # Windows uses '-n', Linux/macOS use '-c' for count
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # 2. Construct the command as a list
    # Security: By passing a list to subprocess.run, arguments are passed 
    # directly to the executable, bypassing the shell. This prevents 
    # command injection even if validation failed.
    command = ['ping', param, '1', host]
    
    print(f"\n--- Pinging {host}... ---")
    
    try:
        # 3. Execute without shell=True
        # capture_output=True allows us to hide raw output and just show status
        # text=True decodes the output to string
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5 # Prevent hanging indefinitely
        )
        
        if result.returncode == 0:
            print(f"[SUCCESS] Host '{host}' is reachable.")
            # Optional: Print latency line if needed, safely parsed
            # print(result.stdout.splitlines()[1]) 
        else:
            print(f"[FAILURE] Host '{host}' is unreachable.")
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Connection to '{host}' timed out.")
    except Exception as e:
        print(f"[ERROR] Could not execute ping: {e}")

def main():
    print("--- Safe Host Reachability Checker ---")
    
    while True:
        host_input = get_input("\nEnter hostname or IP to check (or 'q' to quit): ")
        
        if host_input.lower() == 'q':
            print("Exiting...")
            break
        
        if not host_input:
            continue

        # 1. Validate Input Pattern
        if validate_host_format(host_input):
            # 2. Perform Safe Check
            check_reachability(host_input)
        else:
            print("[SECURITY WARNING] Invalid format detected.")
            print("Only letters, numbers, dots, hyphens, and colons are allowed.")
            print("Input cannot contain spaces or special characters like ';', '&', '|'.")

if __name__ == "__main__":
    main()