import sys
import traceback

from utils.menu import select_destination, select_origin
from utils.misc import remove_local_files
from utils.output import bye, welcome
from utils.scp_connect import scp


def main() -> None:
    """
    Main function that executes the file transfer process.

    This function performs the following steps:
    1. Displays a welcome message.
    2. Prompts the user to select the origin files.
    3. Prompts the user to select the destination folder.
    4. Copies the selected files to the destination folder.
    5. If the copy operation is successful, prompts the user to remove the local files.
    6. Displays a farewell message and exits the program.

    If the user presses Ctrl+C, the program exits immediately.
    If any other exception occurs, the program prints the exception and exits.
    """
    try:
        welcome()
        origin_items = select_origin()
        destination = select_destination()
        scp_completed = scp(origin_items, destination)
        if scp_completed:
            remove_local_files(origin_items)

        bye()

    except KeyboardInterrupt:
        sys.exit()

    except Exception as general_error:
        print(f"A general error occurred: {general_error}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
