import os
import shutil
import subprocess
import sys
import traceback

from pathlib import Path

from paramiko import SSHClient
from pyfiglet import Figlet
from scp import SCPClient
from simple_term_menu import TerminalMenu
from termcolor import colored

from load_config import (
    base_folder,
    destination_base_folder,
    origin_folder,
    series_folder,
    server_name,
    server_user,
)


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
    Check the available space on the destination_base_folder in the server.
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


def format_size(bytes: float) -> str:
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


def print_files_to_copy(origin_files: list) -> None:
    """
    Print the files that are about to be copied.

    Args:
        origin_files (list): The list of origin files. Each item in the list is a
        dictionary where the key is the origin folder and the value is a list of
        file names.
    """
    for full_item in origin_files:
        for file_names in full_item.values():
            for file_name in file_names:
                msg: str = colored(f"- {file_name}", "cyan", attrs=["bold"])
                print(msg)


def collect_file_names(origin_files: list) -> list:
    """
    Collect all file names to be copied.

    Args:
        origin_files (list): The list of origin files. Each item in the list is a
        dictionary where the key is the origin folder and the value is a list of
        file names.

    Returns:
        list: The list of source files to be copied. Each item in the list is a tuple
        where the first element is the source file path and the second element is the
        file name.
    """
    return [
        (f"{origin_folder}/{origin_file}", origin_file)
        for full_item in origin_files
        for origin_folder, origin_files in full_item.items()
        for origin_file in origin_files
    ]


def establish_ssh_and_scp(origin_files: list, destination_folder: str) -> None:
    """
    Establish SSH connection and initiate SCP transfer.

    Args:
        origin_files (list): The list of origin files. Each item in the list is a
        dictionary where the key is the origin folder and the value is a list of
        file names.
        destination_folder (str): The path to the destination folder on the server.

    Raises:
        Exception: If there is an error with the SSH connection.
    """
    print(colored("Copying...", "green", attrs=["bold"]))
    try:
        with SSHClient() as ssh:
            ssh.load_system_host_keys()
            ssh.connect("totoro")
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


def bye(goodbye_msg="\nFarewell!\n") -> None:
    """
    Display a farewell message and exit the program.

    Args:
        goodbye_msg (str): The farewell message to display. Defaults to "\nFarewell!\n".
    """
    msg: str = colored(goodbye_msg, "red", attrs=["bold"])
    print(msg)
    sys.exit(1)


def welcome() -> None:
    """
    Display a welcome message and banner.

    This function clears the terminal screen and prints a welcome banner and message.
    """
    os.system("clear")
    # lean isometric poison alligator
    fig: Figlet = Figlet(font="larry3d")
    banner: str = colored(fig.renderText(" CP2TOTO "), "cyan")
    print(banner)

    welcome_text: str = colored(
        "\nPlease select the files/folders you want to copy to totoro: (SPACE to select, "
        "UP/DOWN to move, ENTER to continue)\n",
        "red",
        attrs=["bold"],
    )
    print(welcome_text)
    print("-" * 90)


def mount_ask() -> None:
    """
    Prompt the user to mount the media folder.

    This function asks the user if they want to mount the media folder. If the user
    agrees, the function mounts the media folder. If the user disagrees, the function
    displays a farewell message and exits the program.
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


def get_list_of_items(folder_path: str) -> list:
    """
    Get a list of items (directories and files) in the given folder path.

    This function returns a sorted list of directories and files in the given folder path.
    If the folder is not found, the function prompts the user to mount the media folder
    and then tries to get the list of items again.

    Args:
        folder_path (str): The path of the folder.

    Returns:
        list: A sorted list of directories and files in the folder.
    """
    path: Path = Path(folder_path)
    dirs: list = []
    files: list = []
    try:
        for item in path.iterdir():
            if item.is_dir():
                dirs.append(item.name)
            else:
                files.append(item.name)
    except FileNotFoundError as fnf_error:
        print(f"An error occurred: {fnf_error}")
        mount_ask()
        return get_list_of_items(folder_path)

    return sorted(dirs) + sorted(files)


def menu(selectable_items: list, add_done_option: bool = False) -> list:
    """
    Display a terminal menu and allow the user to select multiple items.

    Args:
        selectable_items (list): The list of items to display in the menu.
        add_done_option (bool, optional): Whether to add a "DONE" option to the menu.
        Defaults to False.

    Returns:
        list: The list of selected items.
    """
    try:
        selectable_items += [".."]

        if add_done_option:
            selectable_items += ["DONE"]

        terminal_menu: TerminalMenu = TerminalMenu(
            selectable_items,
            multi_select=True,
            show_multi_select_hint=True,
        )
        terminal_menu.show()
        return list(terminal_menu.chosen_menu_entries)
    except TypeError:
        raise (KeyboardInterrupt)


def select_destination() -> str:
    """
    Prompt the user to select the destination folder for the file transfer.

    Returns:
        str: The selected destination folder path.
    """
    message: str = colored(
        "Are these files movies or episodes from a serie?", "yellow", attrs=["bold"]
    )
    print(message)
    media_type: list = menu(["movies", "series", "comedy", "documentaries"])
    media_type: str = media_type[0]

    destination: str = f"{destination_base_folder}/{media_type}/"

    if media_type == "series":
        message: str = colored(
            "Please select the serie folder!", "yellow", attrs=["bold"]
        )
        print(message, "\n")
        serie: str = menu(get_list_of_items(series_folder))[0]

        message: str = colored(
            "Please select the season folder!", "yellow", attrs=["bold"]
        )
        print(message, "\n")
        season: str = menu(get_list_of_items(f"{series_folder}/{serie}"))[0]
        destination: str = f"{destination_base_folder}/series/{serie}/{season}/"
    return destination


def select_origin(
    current_folder=origin_folder, pre_selected_items=[], selection_is_done=False
):
    """
    Prompt the user to select the origin folder for the file transfer.

    Args:
        current_folder (str, optional):
            The current folder path. Defaults to origin_folder.
        pre_selected_items (list, optional):
            The list of pre-selected items. Defaults to [].
        selection_is_done (bool, optional):
            Whether the selection is done. Defaults to False.

    Returns:
        list: The list of selected items.
    """

    if selection_is_done:
        return pre_selected_items

    add_done_option = False
    current_folder = str(Path(current_folder).resolve())
    if current_folder == origin_folder:
        add_done_option = True

    selected_items = menu(get_list_of_items(current_folder), add_done_option)
    if not selected_items:
        bye()

    item = selected_items[-1]
    if item == "DONE":
        for selected_item in selected_items[:-1]:
            if not isinstance(selected_item, list):
                selected_item = [selected_item]
            pre_selected_items.append({current_folder: selected_item})
        return select_origin(
            pre_selected_items=pre_selected_items, selection_is_done=True
        )

    elif Path(f"{current_folder}/{item}").is_dir():
        pre_selected_items.append({current_folder: selected_items[:-1]})
        return select_origin(f"{current_folder}/{item}", pre_selected_items)

    # this is when the user doesn't properly select with space, so we just add the item
    # to the list of selected items and continue, assuming it is just "the one file".
    return [{current_folder: [item]}]


def remove_local_files(origin_items: list) -> None:
    """
    Remove the local files after they have been copied via scp.

    Args:
        origin_items (list): The list of origin items.
    """

    item_paths = []

    for full_item in origin_items:
        for folder, files in full_item.items():
            if folder == origin_folder:
                for origin_file in files:
                    item_paths.append(Path(folder, origin_file).resolve())
            else:
                item_paths.append(Path(folder).resolve())

    message = colored("\nFiles to be removed:\n", "red")
    print(message)
    for item_path in item_paths:
        is_folder_warning = (
            colored("(directory)", "cyan") if Path(item_path).is_dir() else ""
        )
        message = colored(f" - {item_path} {is_folder_warning}", "red")
        print(message)

    remove_local_files: str = input(
        "\nDo you want to remove the local files? (check paths above) [y/n]: "
    )
    if remove_local_files.lower() in ["y", "yes"]:
        print()
        for item_path in item_paths:
            if Path(item_path).is_dir():
                shutil.rmtree(Path(item_path).resolve())
            else:
                os.remove(Path(item_path).resolve())

            prefix_message = colored("Removed:", "red")
            message = colored(Path(item_path).resolve(), "cyan")
            print(f"{prefix_message} {message}")
    else:
        print("Not removing local files!")
