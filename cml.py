import argparse
import requests


def get_pwmanager():
    response = requests.get(f"http://127.0.0.1:8000/pwmanager") #requesting from data from url
    if response.status_code == 200:
        print("Passwords:")
        for pw in response.json().get('data', []):
            print(f" - {pw}")
    else:
        print(f"Failed to fetch passwords: {response.text}")

def create_pw(password_type, password):
    response = requests.post(f"http://127.0.0.1:8000/pwmanager", json={"Type": password_type, "Password": password})
    if response.status_code == 201:
        print("Password created successfully")
    else:
        print(f"Failed to create password: {response.text}")

def delete_all_pw():
    response = requests.delete(f"http://127.0.0.1:8000/delete_all")
    if response.status_code == 204:
        print("All passwords deleted successfully")
    else:
        print(f"Failed to delete passwords: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="CLI for PassGuard")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("get", help="Get all passwords")

    # Subcommand for creating a password
    create_parser = subparsers.add_parser("create", help="Create a new password")
    create_parser.add_argument("type", help="Type of the password")
    create_parser.add_argument("password", help="The password to be created")

    # Subcommand for deleting all passwords
    subparsers.add_parser("delete", help="Delete all passwords")

    args = parser.parse_args()

    if args.command == "get":
        get_pwmanager()
    elif args.command == "create":
        create_pw(args.type, args.password)
    elif args.command == "delete":
        delete_all_pw()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
