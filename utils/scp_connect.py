import os

from utils.misc import confirmation_flow, conversion_flow
from utils.ssh_operations import (
    check_files,
    check_space,
    establish_ssh_and_scp,
    set_permissions,
)


def scp(origin_files: list, destination_folder: str) -> None:
    """
    Securely copy files from the local system to a remote server using SCP.

    This function performs the following steps:
    1. Clears the terminal screen and asks the user if they want to convert the files to
       mp4 with H.265 codec before copying.
    2. If the user confirms, the conversion is performed and the list of origin files is
       updated.
    3. The function then prompts the user to confirm the file transfer. If the user
       confirms, the SCP transfer is initiated with a progress bar.
    4. After the transfer is complete, the function sets the permissions of the files on
       the server, checks if the files have been transferred correctly, and checks the
       available space on the server.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.
        destination_folder (str): The path to the destination folder on the server.

    Raises:
        Exception: If there is an error with the SSH connection.
    """
    os.system("clear")
    origin_files = conversion_flow(origin_files)

    if confirmation_flow(origin_files, destination_folder):
        establish_ssh_and_scp(origin_files, destination_folder)
        set_permissions(destination_folder)
        check_files(origin_files, destination_folder)
        check_space()
        return True
