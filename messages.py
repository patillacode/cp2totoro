import os
import sys

from pyfiglet import Figlet
from termcolor import colored


def bye(good_bye_msg="\nFarewell!\n") -> None:
    """
    Display a farewell message and exit the program.

    Args:
        good_bye_msg (str): The farewell message to display. Defaults to "\nFarewell!\n".
    """
    msg: str = colored(good_bye_msg, "red", attrs=["bold"])
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
