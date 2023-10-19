import os
import shutil

from pathlib import Path

from termcolor import colored

from utils.config import origin_folder


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
        (f"{source_folder}/{source_file}", source_file)
        for full_item in origin_files
        for source_folder, source_files in full_item.items()
        for source_file in source_files
    ]


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
