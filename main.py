import os

application_name: str = "EIS Grade Notifier"


# Display Main Menu
def display_main_menu():
    print("Main Menu\n")
    print("1. Login")
    print("2. Help")
    print("3. Exit")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            clear()
            print("Logged in")
            break
        elif choice == "2":
            display_help()
            break
        elif choice == "3":
            print("Goodbye")
            break
        else:
            print("Invalid choice")
            continue


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Display Help Menu
def display_help():
    print("Help Menu\n\n")
    print("""
    You first need to login to your EIS account.\n
    Then you need to get your PHPSESSID cookie.\n
    You can do this by using this chrome extension:\n
    https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg\n
    0. Back\n
    """)
    while True:
        choice = input("Enter your choice: ")
        if choice == "0":
            clear()
            display_main_menu()
            break
        else:
            clear()
            print("Invalid choice")
            continue


def run():
    print("Welcome to the EIS Grade Notifier")
    display_main_menu()


def main():
    run()


if __name__ == "__main__":
    main()
