import sys


def get_user_confirmation(message: str) -> None:
    response: str = input(message)
    if not response.lower().strip().startswith("y"):
        print("Aborting!")
        sys.exit()
