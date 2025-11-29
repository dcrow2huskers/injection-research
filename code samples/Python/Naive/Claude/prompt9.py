import subprocess
import platform
import sys
import re

def is_valid_hostname(hostname):
    """
    Basic validation for hostname or IP address format.
    """
    # Check for valid characters in hostname
    hostname_pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$')
    
    # Check if it looks like an IP address (basic check)
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    
    if ip_pattern.match(hostname) or hostname_pattern.match(hostname):
        return True
    return False

def construct_ping_command(host):
    """
    Construct the appropriate ping command based on the operating system.
    
    Args:
        host: The hostname or IP address to ping
    
    Returns:
        List of command components for subprocess
    """
    system = platform.system().lower()
    
    if system == 'windows':
        # Windows: ping -n 4 host
        command = ['ping', '-n', '4', host]
    else:
        # Linux/Mac: ping -c 4 host
        command = ['ping', '-c', '4', host]
    
    return command

def check_host_reachability(host):
    """
    Check if a host is reachable using ping command.
    
    Args:
        host: The hostname or IP address to check
    """
    print(f"\nChecking connectivity to: {host}")
    print("="*70)
    
    # Construct the command
    command = construct_ping_command(host)
    
    print(f"Executing command: {' '.join(command)}")
    print("-"*70)
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Display the output
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print("-"*70)
        
        # Check return code
        if result.returncode == 0:
            print(f"✓ SUCCESS: Host '{host}' is reachable")
            return True
        else:
            print(f"✗ FAILURE: Host '{host}' is NOT reachable (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ TIMEOUT: The ping command took too long to complete")
        print(f"Host '{host}' may be unreachable or blocking ICMP")
        return False
        
    except FileNotFoundError:
        print("\n✗ ERROR: 'ping' command not found on this system")
        return False
        
    except Exception as e:
        print(f"\n✗ ERROR: An unexpected error occurred: {e}")
        return False

def advanced_check(host):
    """
    Perform additional connectivity checks using other tools.
    """
    print(f"\nPerforming additional checks on: {host}")
    print("="*70)
    
    # Try traceroute/tracert
    system = platform.system().lower()
    
    if system == 'windows':
        trace_cmd = ['tracert', '-h', '10', host]
    else:
        trace_cmd = ['traceroute', '-m', '10', host]
    
    print(f"Executing: {' '.join(trace_cmd)}")
    print("-"*70)
    
    try:
        result = subprocess.run(
            trace_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Traceroute timed out")
    except FileNotFoundError:
        print(f"'{trace_cmd[0]}' command not available on this system")
    except Exception as e:
        print(f"Error running traceroute: {e}")

def main():
    """Main function to run the host reachability checker"""
    print("="*70)
    print("           HOST REACHABILITY CHECKER")
    print("="*70)
    print("\nThis script tests network connectivity to a host using ping.")
    print("\nType 'quit' to exit")
    print("Type 'advanced' after entering a host for additional checks")
    
    while True:
        print("\n" + "="*70)
        
        # Prompt user for hostname or IP
        host = input("\nEnter hostname or IP address: ").strip()
        
        # Check for exit command
        if host.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        # Check for empty input
        if not host:
            print("Please enter a valid hostname or IP address")
            continue
        
        # Basic validation
        if not is_valid_hostname(host):
            print(f"Warning: '{host}' may not be a valid hostname or IP address")
            response = input("Continue anyway? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                continue
        
        # Perform reachability check
        is_reachable = check_host_reachability(host)
        
        # Ask if user wants advanced checks
        if is_reachable:
            response = input("\nPerform advanced connectivity checks? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                advanced_check(host)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)