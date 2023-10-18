import os
import shutil
import sys

from pathlib import Path

import yaml

from simple_term_menu import TerminalMenu
from termcolor import colored

from messages import bye


def read_config():
    with open("configuration.yaml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


config = read_config()

origin_folder: str = config["folders"]["origin"]
series_folder: str = config["folders"]["series"]
comedy_folder: str = config["folders"]["comedy"]
destination_base_folder: str = config["folders"]["destination_base"]


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
                "sudo mount -o rw -t nfs totoro:/opt/mounts/media "
                "/Users/dvitto/media/mounts/media"
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
