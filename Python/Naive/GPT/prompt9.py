import subprocess
import platform

def main():
    host = input("Enter a hostname or IP address to check reachability: ").strip()

    # Choose correct ping parameters depending on OS
    if platform.system().lower().startswith("win"):
        cmd = ["ping", "-n", "4", host]
    else:
        cmd = ["ping", "-c", "4", host]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("\n--- Command Output ---")
        print(result.stdout if result.stdout else "(No output)")
        if result.stderr:
            print("\n--- Errors ---")
            print(result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()