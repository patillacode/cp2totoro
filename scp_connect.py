import subprocess

from paramiko import SSHClient
from rich.progress import Progress
from scp import SCPClient
from termcolor import colored


def set_permissions(destination_folder: str) -> None:
    """
    Set permissions on copied files.

    This function sets the permissions of the copied files in the destination folder to 755.

    Args:
        destination_folder (str): The destination folder path.
    """
    print(colored("\nSetting permissions on copied files...", "red", attrs=["bold"]))
    subprocess.run(["ssh", "dvitto@totoro", f'chmod -R 755 "{destination_folder}"'])


def check_files(origin_files: list, destination_folder: str) -> None:
    """
    Check files in the destination folder.

    This function checks the files in the destination folder against the list of origin files.
    It prints the details of each file in the destination folder.

    Args:
        origin_files (list): The list of origin files.
        destination_folder (str): The destination folder path.
    """
    print(colored("Checking files...", "green", attrs=["bold"]))
    for full_item in origin_files:
        for file_names in full_item.values():
            for file_name in file_names:
                subprocess.run(
                    ["ssh", "dvitto@totoro", f'ls -alh "{destination_folder}{file_name}"']
                )


def check_space() -> None:
    """
    Check the available space on the server.
    """
    space_left: bytes = subprocess.check_output(
        ["ssh", "dvitto@totoro", "df -h /opt/mounts/media/ | awk 'NR>1{print $4}'"]
    )
    msg: str = colored("Space left", "green", attrs=["bold"])
    space_left_msg: str = colored(space_left.decode("utf-8"), "red", attrs=["bold"])
    print(f"{msg}: {space_left_msg}")


def scp(origin_files: list, destination_folder: str) -> None:
    """
    Copy files using SCP with progress bar.

    Args:
        origin_files (list): The list of origin files.
        destination_folder (str): The destination folder path.
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

        with SSHClient() as ssh:
            ssh.load_system_host_keys()
            ssh.connect("totoro")

            with SCPClient(ssh.get_transport()) as scp:
                # Prepare the list of source files to be copied
                source_files: list = [
                    (f"{origin_folder}/{origin_file}", origin_file)
                    for full_item in origin_files
                    for origin_folder, origin_files in full_item.items()
                    for origin_file in origin_files
                ]

                # Copy files to the destination folder with progress bar
                with Progress() as progress:
                    task = progress.add_task("[cyan]Progress:", total=len(source_files))

                    for source_file, file_name in source_files:
                        scp.put(source_file, remote_path=destination_folder)
                        file_msg: str = colored(f"{file_name}", "cyan", attrs=["bold"])
                        icon: str = colored("􀆅", "green", attrs=["bold"])
                        print(f"{file_msg} {icon}")
                        progress.advance(task)

        # Set permissions, check files, and check space
        set_permissions(destination_folder)
        check_files(origin_files, destination_folder)
        check_space()
        return True
