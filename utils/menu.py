from pathlib import Path

from simple_term_menu import TerminalMenu
from termcolor import colored

from utils.config import destination_base_folder, origin_folder, series_folder
from utils.output import bye
from utils.ssh_operations import mount_ask


def get_list_of_items(folder_path: str) -> list:
    """
    Retrieve and return a sorted list of items (directories and files) from a specified
    folder path.

    If the specified folder is not found, the function prompts the user to mount the media
    folder and attempts to retrieve the list of items again.

    Args:
        folder_path (str): The path of the folder from which to retrieve items.

    Returns:
        list: A sorted list of directories and files in the specified folder.
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
    Display a terminal menu with a list of selectable items and allow the user to make
    multiple selections.

    The function also provides an option to add a "DONE" option to the menu, which can be
    used to indicate the completion of the selection process.

    Args:
        selectable_items (list): The list of items to be displayed in the menu for
        selection.
        add_done_option (bool, optional): A flag indicating whether to add a "DONE"
        option to the menu. Defaults to False.

    Returns:
        list: The list of items selected by the user.
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
    Interactively prompt the user to select the destination folder for the file transfer.

    The function first asks the user to specify the type of media (movies, series, comedy,
    documentaries), and then, if the media type is 'series',
    it further asks the user to select the series and season folders.

    Returns:
        str: The path of the selected destination folder.
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
    Interactively prompt the user to select the origin files for the file transfer.

    The function allows the user to navigate through the directory structure and select
    multiple files. The selection process can be terminated by selecting the "DONE" option

    Args:
        current_folder (str, optional): The current folder path. Defaults to origin_folder
        pre_selected_items (list, optional): The list of items that have been pre-selected
                                             Defaults to [].
        selection_is_done (bool, optional): A flag indicating whether the selection
                                            process is complete. Defaults to False.

    Returns:
        list: A list of dictionaries, where each dictionary represents a folder and
        contains the selected items from that folder.
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
