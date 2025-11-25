import subprocess
import shlex
import os

def main():
    search_term = input("Enter search term: ").strip()
    directory = input("Enter directory to search: ").strip()

    # Validate directory
    if not os.path.isdir(directory):
        print("Error: That directory does not exist.")
        return

    # Safely quote arguments
    safe_term = shlex.quote(search_term)
    safe_dir = shlex.quote(directory)

    # Construct the grep command
    command = f"grep -Rni {safe_term} {safe_dir}"

    print("\nConstructed command:")
    print(command)
    print("\n--- Search Results ---\n")

    try:
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True
        )

        # Print results
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

    except Exception as e:
        print("An error occurred while running the command:", e)


if __name__ == "__main__":
    main()