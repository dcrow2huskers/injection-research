#!/usr/bin/env python3
"""
Secure host reachability checker.

- Prompts the user for a hostname or IP address.
- Validates the input against safe patterns (IPv4, IPv6, or hostname).
- Uses a secure method (no shell, no raw command strings) to run ping.
- Presents a simple, safe result message.
"""

import ipaddress
import platform
import re
import subprocess
import sys


def is_valid_ip(address: str) -> bool:
    """Return True if address is a valid IPv4 or IPv6 literal."""
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


# Simple, restrictive hostname regex:
# - Labels: 1–63 chars of letters, digits, or hyphens
# - Labels separated by dots
# - Total length up to 253 chars
HOSTNAME_REGEX = re.compile(
    r"^(?=.{1,253}$)([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\."
    r"([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$"
)


def is_valid_hostname(name: str) -> bool:
    """Return True if name looks like a valid DNS hostname."""
    if not name or name.endswith("."):  # disallow trailing dot for simplicity
        return False
    return HOSTNAME_REGEX.match(name) is not None


def validate_target(target: str) -> bool:
    """Validate user input as either IP or hostname."""
    target = target.strip()
    if not target:
        return False
    if is_valid_ip(target):
        return True
    if is_valid_hostname(target):
        return True
    return False


def ping_host(target: str, timeout_seconds: int = 5) -> bool:
    """
    Use the system ping command with a safe, argument-list invocation.
    - No shell usage.
    - No raw command string concatenation.
    Returns True if ping succeeds (exit code 0), else False.
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows ping: -n 1 (one echo), -w timeout(ms)
        cmd = ["ping", "-n", "1", "-w", str(timeout_seconds * 1000), target]
    else:
        # POSIX ping: -c 1 (one echo), -W timeout(seconds) on Linux,
        # but -W is ignored on some platforms; we also use subprocess timeout.
        cmd = ["ping", "-c", "1", "-W", str(timeout_seconds), target]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,  # don't show raw command output
            stderr=subprocess.DEVNULL,
            timeout=timeout_seconds + 2,
            check=False,               # we interpret returncode ourselves
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        # OSError: ping not found or not executable
        # TimeoutExpired: no response in time
        return False


def main() -> None:
    print("Secure Host Reachability Checker")
    print("--------------------------------")

    target = input("Enter a hostname or IP address to check: ").strip()

    if not validate_target(target):
        print("\n[!] The value you entered is not a valid hostname or IP address.")
        print("    Please use only standard DNS hostnames or numeric IP addresses.")
        sys.exit(1)

    print(f"\nChecking reachability for: {target!r} ...")

    reachable = ping_host(target)

    # Present a simple, safe result without echoing raw system output.
    if reachable:
        print(f"[OK] The host {target!r} appears to be reachable.")
    else:
        print(f"[X] The host {target!r} does not appear to be reachable.")
        print("    This could mean it is down, blocking ping, or unreachable from this system.")


if __name__ == "__main__":
    main()