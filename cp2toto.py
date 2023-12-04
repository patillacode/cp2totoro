import sys
import traceback

from utils.menu import select_destination, select_origin
from utils.misc import conversion_flow, remove_local_files
from utils.output import bye, welcome
from utils.scp_connect import scp


def main() -> None:
    """
    This is the main function that orchestrates the file transfer process.

    The function follows these steps:
    1. Displays a welcome message to the user.
    2. Prompts the user to select the files they want to transfer (origin files).
    3. Asks the user to specify the destination folder where the files will be transferred
    4. Initiates file transfer process, copying selected files to the destination folder.
    5. If successful, it asks the user if they want to remove the original files.
    6. Finally, the function displays a farewell message and terminates the program.

    The function handles two types of exceptions:
    - KeyboardInterrupt:
        If the user interrupts the program (e.g., by pressing Ctrl+C), the function
        immediately exits.
    - General exceptions:
        If any other type of exception occurs, the function prints the exception details
        and exits with a status code of 1.
    """
    try:
        welcome()
        origin_files = select_origin()
        destination_folder = select_destination()
        origin_files = conversion_flow(origin_files)
        scp_completed = scp(origin_files, destination_folder)
        if scp_completed:
            remove_local_files(origin_files)

        bye()

    except KeyboardInterrupt:
        sys.exit()

    except Exception as general_error:
        print(f"A general error occurred: {general_error}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
