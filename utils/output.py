import os
import sys

from pyfiglet import Figlet
from termcolor import colored

from utils.misc import format_size


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
