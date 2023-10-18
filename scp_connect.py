import subprocess
import sys
import traceback

from paramiko import SSHClient
from scp import SCPClient
from termcolor import colored

from utils import read_config

config = read_config()
server_user = config["server"]["user"]
server_name = config["server"]["name"]


def set_permissions(destination_folder: str) -> None:
    """
    Set permissions on copied files.

    This function sets the permissions of the copied files in the destination folder
    to be 755 using the chmod command via ssh.

    Args:
        destination_folder (str): The destination folder path on the server.

    Raises:
        subprocess.CalledProcessError: If the subprocess call to ssh fails.
    """
    print(colored("\nSetting permissions on copied files...", "red", attrs=["bold"]))
    subprocess.run(
        ["ssh", f"{server_user}@{server_name}", f'chmod -R 755 "{destination_folder}"']
    )


def check_files(origin_files: list, destination_folder: str) -> None:
    """
    Check files in the destination folder.

    This function checks the files in the destination folder against the list of
    origin files. It uses the 'ls -alh' command via ssh to print the details of each
    file in the destination folder.

    Args:
        origin_files (list): The list of origin files. Each item in the list is a
        dictionary where the key is the origin folder and the value is a list of
        file names.
        destination_folder (str): The destination folder path on the server.

    Raises:
        subprocess.CalledProcessError: If the subprocess call to ssh fails.
    """
    print(colored("Checking files...", "green", attrs=["bold"]))
    for full_item in origin_files:
        for file_names in full_item.values():
            for file_name in file_names:
                subprocess.run(
                    [
                        "ssh",
                        f"{server_user}@{server_name}",
                        f'ls -alh "{destination_folder}{file_name}"',
                    ]
                )


def check_space() -> None:
    """
    Check the available space on the server.
    """
    base_folder = config["server"]["base_folder"]
    awk = "awk 'NR>1{print $4}'"
    space_left: bytes = subprocess.check_output(
        [
            "ssh",
            f"{server_user}@{server_name}",
            (f"df -h {base_folder} | {awk}"),
        ]
    )
    msg: str = colored("Space left", "green", attrs=["bold"])
    space_left_msg: str = colored(space_left.decode("utf-8"), "red", attrs=["bold"])
    print(f"{msg}: {space_left_msg}")


def format_size(bytes):
    """
    Format bytes into a human-readable format.

    Args:
        bytes (int): The number of bytes.

    Returns:
        str: The number of bytes in a human-readable format.
    """
    sizes = ["B", "KB", "MB", "GB", "TB"]
    for size in sizes:
        if bytes < 1024.0:
            return f"{bytes:.2f} {size}"
        bytes /= 1024.0
    return f"{bytes:.2f} {sizes[-1]}"


def print_progress(filename, size, sent) -> None:
    """
    Print the progress of the SCP transfer.

    Args:
        filename (str): The name of the file being transferred.
        size (int): The size of the file being transferred.
        sent (int): The number of bytes transferred.
    """
    filename = colored(
        f"{filename.decode('utf-8')}",
        "yellow",
        attrs=["bold"],
    )
    progress = colored(
        f"{int(float(sent) / float(size) * 100)}%",
        "green",
        attrs=["bold"],
    )
    print(f"{filename} ({format_size(size)}): {progress} {' ' * 10}\r", end="")


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

    # Collect all file names to be copied
    for full_item in origin_files:
        for file_names in full_item.values():
            for file_name in file_names:
                msg: str = colored(f"- {file_name}", "cyan", attrs=["bold"])
                print(msg)

    confirmation: str = input("Confirm to copy [y/n]:")

    if confirmation in ["y", "Y", "yes"]:
        print(colored("Copying...", "green", attrs=["bold"]))

        try:
            with SSHClient() as ssh:
                ssh.load_system_host_keys()
                ssh.connect("totoro")
                with SCPClient(ssh.get_transport(), progress=print_progress) as scp:
                    # Prepare the list of source files to be copied
                    source_files: list = [
                        (f"{origin_folder}/{origin_file}", origin_file)
                        for full_item in origin_files
                        for origin_folder, origin_files in full_item.items()
                        for origin_file in origin_files
                    ]

                    # Copy files to the destination folder with progress bar
                    for source_file, file_name in source_files:
                        scp.put(source_file, remote_path=destination_folder)
                        file_msg: str = colored(f"{file_name}", "cyan", attrs=["bold"])
                        icon: str = colored("􀆅", "green", attrs=["bold"])
                        print(f"{file_msg} {icon} {' ' * 30}")

        except Exception as ssh_error:
            print(f"An error occurred with the ssh connection: {ssh_error}")
            traceback.print_exc()
            sys.exit(1)

        set_permissions(destination_folder)
        check_files(origin_files, destination_folder)
        check_space()
        return True
