import os
import subprocess
import sys
import traceback

from paramiko import SSHClient
from scp import SCPClient
from termcolor import colored

from utils.config import base_folder, destination_base_folder, server_name, server_user
from utils.output import bye, print_progress


def collect_file_names(origin_files: list) -> list:
    """
    Collects all file names to be copied from the local system to the remote server.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.

    Returns:
        list: A list of tuples. Each tuple contains the source file path and the file name
    """
    return [
        (f"{origin_folder}/{origin_file}", origin_file)
        for full_item in origin_files
        for origin_folder, origin_files in full_item.items()
        for origin_file in origin_files
    ]


def establish_ssh_and_scp(origin_files: list, destination_folder: str) -> None:
    """
    Establishes an SSH connection and initiates an SCP transfer.

    This function establishes an SSH connection to the remote server and initiates an SCP
    transfer of the specified files from the local system to the remote server.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.
        destination_folder (str): The path to the destination folder on the server.

    Raises:
        Exception: If there is an error with the SSH connection.
    """
    print(colored("Copying...", "green", attrs=["bold"]))
    try:
        with SSHClient() as ssh:
            ssh.load_system_host_keys()
            ssh.connect(server_name)
            with SCPClient(ssh.get_transport(), progress=print_progress) as scp:
                source_files: list = collect_file_names(origin_files)

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


def set_permissions(destination_folder: str) -> None:
    """
    Sets permissions on copied files.

    This function sets the permissions of the copied files in the destination folder
    on the remote server to be 755 using the chmod command via ssh.

    Args:
        destination_folder (str): The path to the destination folder on the server.

    Raises:
        subprocess.CalledProcessError: If the subprocess call to ssh fails.
    """
    print(colored("\nSetting permissions on copied files...", "red", attrs=["bold"]))
    subprocess.run(
        ["ssh", f"{server_user}@{server_name}", f'chmod -R 755 "{destination_folder}"']
    )


def check_files(origin_files: list, destination_folder: str) -> None:
    """
    Checks files in the destination folder.

    This function checks the files in the destination folder on the remote server against
    the list of origin files. It uses the 'ls -alh' command via ssh to print the details
    of each file in the destination folder.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.
        destination_folder (str): The path to the destination folder on the server.

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
    Checks the available space on the destination_base_folder in the server.

    This function checks the available disk space on the destination_base_folder on the
    remote server and prints it to the console.
    """
    awk = "awk 'NR>1{print $4}'"
    space_left: bytes = subprocess.check_output(
        [
            "ssh",
            f"{server_user}@{server_name}",
            (f"df -h {destination_base_folder} | {awk}"),
        ]
    )
    msg: str = colored("Space left", "green", attrs=["bold"])
    space_left_msg: str = colored(space_left.decode("utf-8"), "red", attrs=["bold"])
    print(f"{msg}: {space_left_msg}")


def mount_ask() -> None:
    """
    Prompts the user to mount the media folder.

    This function asks the user if they want to mount the media folder on the local system
    If the user agrees, the function mounts the media folder. If the user disagrees, the
    function displays a farewell message and exits the program.
    """
    mount: str = input("Do you want to mount the media folder? [y/n]: ")
    if mount.lower() in ["", "y", "yes"]:
        message: str = colored("Mounting... (enter password)", "yellow", attrs=["bold"])
        print(message)
        os.system(
            (
                f"sudo mount -o rw -t nfs {server_name}:{destination_base_folder} "
                f"{base_folder}"
            )
        )
    else:
        bye("Ok, not mounting anything! Bye!")
        sys.exit()
