import os
import subprocess
import shlex

def main():
    directory = input("Enter the directory path to clean: ").strip()

    if not os.path.isdir(directory):
        print("Error: That path is not a valid directory.")
        return

    print(f"\nWARNING: This will remove *all files* inside:\n  {directory}\n")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cleanup canceled.")
        return

    # Construct a safe shell command
    # Only deletes files directly inside the directory, not recursively.
    command = f"rm -f {shlex.quote(directory)}/*"

    print(f"\nRunning command:\n  {command}\n")

    try:
        # Execute the command
        subprocess.run(command, shell=True, check=True)
        print("Cleanup complete.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while cleaning the directory:")
        print(e)

if __name__ == "__main__":
    main()