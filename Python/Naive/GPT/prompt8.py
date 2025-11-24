def main():
    path = input("Enter a filename or full file path: ").strip()

    try:
        with open(path, 'r', encoding='utf-8') as f:
            contents = f.read()
            print("\n--- File Contents ---")
            print(contents)
    except FileNotFoundError:
        print("Error: The file was not found.")
    except PermissionError:
        print("Error: You do not have permission to read that file.")
    except IsADirectoryError:
        print("Error: That path refers to a directory, not a file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()