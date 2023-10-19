from termcolor import colored

from utils.output import print_files_to_copy
from utils.ssh_operations import (
    check_files,
    check_space,
    establish_ssh_and_scp,
    set_permissions,
)


def scp(origin_files: list, destination_folder: str) -> None:
    """
    Copy files from the origin to the destination using SCP with a progress bar.

    This function performs the following steps:
    1. Prints a message indicating the files/folders to be copied.
    2. Collects all file names to be copied.
    3. Prompts the user for confirmation to copy.
    4. If confirmed, initiates the SCP transfer with a progress bar.
    5. On successful transfer, sets permissions, checks files, and checks space on
        the server.

    Args:
        origin_files (list): The list of origin files. Each item in the list is a
        dictionary where the key is the origin folder and the value is a list of
        file names.
        destination_folder (str): The path to the destination folder on the server.

    Raises:
        Exception: If there is an error with the SSH connection.
    """

    msg: str = colored(
        "You are about to copy the following files/folders into", "yellow", attrs=["bold"]
    )
    destination_msg: str = colored(destination_folder, "red", attrs=["bold"])
    print(msg, destination_msg)

    print_files_to_copy(origin_files)

    confirmation: str = input("Confirm to copy [y/n]:")
    if confirmation in ["y", "Y", "yes"]:
        establish_ssh_and_scp(origin_files, destination_folder)
        set_permissions(destination_folder)
        check_files(origin_files, destination_folder)
        check_space()
        return True
