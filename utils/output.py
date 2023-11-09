import os
import sys

from pyfiglet import Figlet
from termcolor import colored

from utils.config import server_name
from utils.misc import format_size


def print_progress(filename, size, sent) -> None:
    """
    Display the progress of the SCP file transfer.

    This function prints the name of the file being transferred, its size, and the
    percentage of bytes transferred so far.

    Args:
        filename (str): The name of the file being transferred.
        size (int): The total size of the file being transferred in bytes.
        sent (int): The number of bytes that have been transferred so far.
    """
    filename = colored(
        f" {filename.decode('utf-8')}",
        "yellow",
        attrs=["bold"],
    )
    progress = colored(
        f"{int(float(sent) / float(size) * 100)}%",
        "green",
        attrs=["bold"],
    )
    print(f"{filename} ({format_size(size)}): {progress} {' ' * 10}\r", end="")


def bye(goodbye_msg="\nFarewell!\n") -> None:
    """
    Display a farewell message and terminate the program.

    This function prints a farewell message to the console and then terminates the
    program using sys.exit(1).

    Args:
        goodbye_msg (str): The farewell message to be displayed.
        Defaults to "Farewell!".
    """
    msg: str = colored(goodbye_msg, "red", attrs=["bold"])
    print(msg)
    sys.exit(1)


def welcome() -> None:
    """
    Display a welcome message and banner.

    This function clears the terminal screen and prints a welcome banner and a message
    instructing the user on how to select files/folders for copying. The banner is
    generated using the 'larry3d' font from the pyfiglet library.
    """
    os.system("clear")
    # lean isometric poison alligator
    fig: Figlet = Figlet(font="larry3d")
    banner: str = colored(fig.renderText(" CP2TOTO "), "cyan")
    print(banner)

    welcome_text: str = colored(
        (
            f"\nPlease select the files/folders you want to copy to {server_name}: "
            "(SPACE to select, UP/DOWN to move, ENTER to continue)\n"
        ),
        "red",
        attrs=["bold"],
    )
    print(welcome_text)
    print("-" * 90)
