import os
import shutil
import sys
import time

from pathlib import Path

import ffmpeg

from termcolor import colored

from utils.config import origin_folder


def print_files_to_copy(origin_files: list) -> None:
    """
    Print the names of the files that are about to be copied.

    Args:
        origin_files (list): A list of dictionaries.
        Each dictionary represents a directory and contains pairs of directory path and
        list of file names in that directory.
    """
    for full_item in origin_files:
        item_folder_path = f"{list(full_item.keys())[0]}"
        for file_names in full_item.values():
            for file_name in file_names:
                file_size = format_size(
                    os.path.getsize(f"{item_folder_path}/{file_name}")
                )
                msg: str = colored(f"- {file_name}", "cyan", attrs=["bold"])
                print(msg, end=" ")
                msg = colored(f"({file_size})", "magenta", attrs=["bold"])
                print(msg)


def get_new_file_name(origin_file: str) -> str:
    """
    Generate a new file name for the converted file.

    Args:
        origin_file (str): The original file path.

    Returns:
        str: The new file path with '_H265.mp4' appended to the original file name.
    """
    origin_file_path = Path(origin_file)
    origin_file_directory = origin_file_path.parent
    origin_file_name = origin_file_path.stem
    return f"{origin_file_directory}/{origin_file_name}_H265.mp4"


def confirmation_flow(origin_files: list, destination_folder: str) -> bool:
    """
    Prompt the user to confirm the file transfer.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.
        destination_folder (str): The destination folder path.

    Returns:
        bool: True if the user confirms the file transfer, False otherwise.
    """
    msg: str = colored(
        "\nYou are about to copy the following files/folders into",
        "yellow",
        attrs=["bold"],
    )
    destination_msg: str = colored(destination_folder, "red", attrs=["bold"])
    print(msg, destination_msg)
    print_files_to_copy(origin_files)
    copy_confirmation: str = input(
        colored("\nConfirm to copy [y/N]: ", "green", attrs=["bold"])
    )
    if copy_confirmation.lower() in ["y", "yes"]:
        return True


def conversion_flow(origin_files: list) -> list:
    """
    Ask the user if they want to convert the files to mp4 with H.265 codec before copying.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.

    Returns:
        list: The updated list of origin files after conversion.
    """
    print(
        colored(
            "\nDo you want to convert the files to mp4 with H.265 codec before copying "
            "them to the server?",
            "yellow",
            attrs=["bold"],
        )
    )
    print(colored("This can be a lengthy process.", "magenta", attrs=["bold"]))
    print_files_to_copy(origin_files)
    convert_confirmation: str = input(
        colored("\nConfirm conversion [y/N]: ", "yellow", attrs=["bold"])
    )
    if convert_confirmation.lower() in ["y", "yes"]:
        new_origin_files = []
        for full_item in origin_files:
            for directory, file_names in full_item.items():
                if file_names:
                    new_origin_dict = {directory: []}
                    for file_name in file_names:
                        new_file_path = convert_to_H265_codec(f"{directory}/{file_name}")
                        new_file = Path(new_file_path)
                        new_origin_dict[directory].append(
                            f"{new_file.stem}{new_file.suffix}"
                        )
                    new_origin_files.append(new_origin_dict)
        origin_files = new_origin_files

    return origin_files


def convert_to_H265_codec(origin_file: str) -> str:
    """
    Convert the given file to mp4 format with H.265 codec.

    Args:
        origin_file (str): The original file path.

    Returns:
        str: The path of the converted file if conversion is successful, otherwise the
        original file path.
    """
    original_size = os.path.getsize(origin_file)
    probe = ffmpeg.probe(origin_file)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream is None:
        print(f"No video stream found in {colored(origin_file, 'red')}")
        return origin_file

    if video_stream["codec_name"] != "hevc":
        new_origin_file = get_new_file_name(origin_file)
        try:
            print(
                (
                    f"\nConverting {colored(origin_file, 'yellow')}\n"
                    "to mp4 with H.265 codec"
                )
            )
            start_time = time.time()
            ffmpeg.input(origin_file).output(
                new_origin_file,
                vcodec="libx265",
                crf=23,
                acodec="aac",
                strict="experimental",
            ).overwrite_output().run(quiet=True)
            end_time = time.time()

        except ffmpeg.Error as err:
            print(
                f"Error occurred while converting {colored(origin_file, 'yellow')} to "
                f"mp4 (H.265): {colored(err, 'red')}"
            )
            sys.exit(1)

        else:
            new_size = os.path.getsize(new_origin_file)
            size_reduction = int(((original_size - new_size) / original_size) * 100)
            space_saved = format_size(original_size - new_size)
            hours, rem = divmod(end_time - start_time, 3600)
            minutes, seconds = divmod(rem, 60)
            formatted_time = "{:0>2}:{:0>2}:{:05.2f}".format(
                int(hours), int(minutes), seconds
            )
            print(f"Conversion time: {colored(formatted_time, 'white', attrs=['bold'])}")
            print(
                f"Space saved: {colored(f'{size_reduction}%', 'magenta', attrs=['bold'])}"
                f" {colored(f'({space_saved})', 'cyan', attrs=['bold'])}"
            )
            return new_origin_file
    else:
        print(
            f"\n{colored(f'{origin_file}', 'yellow')} "
            "\nis already using H.265 codec "
            f"{colored('(skipping conversion)','green',attrs=['bold'])}"
        )
        return origin_file


def format_size(size_bytes: float) -> str:
    """
    Convert a size in bytes to a human-readable format.

    Args:
        size_bytes (float): The size in bytes.

    Returns:
        str: The size in a human-readable format.
    """
    sizes = ["B", "KB", "MB", "GB", "TB"]
    for size in sizes:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {size}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {sizes[-1]}"


def collect_file_names(origin_files: list) -> list:
    """
    Collect all file names to be copied.

    Args:
        origin_files (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.

    Returns:
        list: A list of tuples. Each tuple contains the source file path and the file name
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
        origin_items (list): A list of dictionaries. Each dictionary represents a
        directory and contains pairs of directory path and list of file names in that
        directory.
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
        colored(
            "\nDo you want to remove the local files? (check paths above) [y/N]: ",
            "yellow",
            attrs=["bold"],
        )
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
