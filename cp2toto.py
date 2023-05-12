import os
import subprocess
import sys

from pathlib import Path

from paramiko import SSHClient
from pyfiglet import Figlet
from scp import SCPClient
from simple_term_menu import TerminalMenu
from termcolor import colored

origin_folder = '/Users/dvitto/media/torrents'
series_folder = '/Users/dvitto/media/mounts/media/series'
destination_base_folder = '/opt/mounts/media'


def bye():
    msg = colored('\nFarewell!\n', 'red', attrs=['bold'])
    print(msg)
    sys.exit(1)


def welcome():
    os.system('clear')
    # lean isometric poison alligator
    fig = Figlet(font='larry3d')
    banner = colored(fig.renderText(' CP2TOTO '), 'cyan')
    print(banner)

    welcome_text = colored(
        '\nPlease select the files/folders you want to copy to totoro: (SPACE to select, '
        'UP/DOWN to move, ENTER to continue)\n',
        'red',
        attrs=['bold'],
    )
    print(welcome_text)
    print('-' * 90)


def get_list_of_items(folder_path):
    path = Path(folder_path)
    dirs = []
    files = []
    for item in path.iterdir():
        if item.is_dir():
            dirs.append(item.name)
        else:
            files.append(item.name)
    return sorted(dirs) + sorted(files)


def menu(selectable_items):
    terminal_menu = TerminalMenu(
        selectable_items + ['..'],
        multi_select=True,
        show_multi_select_hint=True,
    )
    terminal_menu.show()
    return terminal_menu.chosen_menu_entries


def select_destination():
    message = colored(
        'Are these files movies or episodes from a serie?', 'yellow', attrs=['bold']
    )
    print(message)
    media_type = menu(['movies', 'series'])

    destination = f'{destination_base_folder}/movies/'

    if media_type[0] == 'series':
        message = colored('Please select the serie folder!', 'yellow', attrs=['bold'])
        print(message, '\n')
        serie = menu(get_list_of_items(series_folder))[0]

        message = colored('Please select the season folder!', 'yellow', attrs=['bold'])
        print(message, '\n')
        season = menu(get_list_of_items(f'{series_folder}/{serie}'))[0]
        destination = f'{destination_base_folder}/series/{serie}/{season}/'

    return destination


def select_origin(current_folder=origin_folder):
    # we start in the `current_folder` (default set as `origin_folder`)
    # we offer the user to choose from the files/folders in there
    selected_items = menu(get_list_of_items(current_folder))

    if not selected_items:
        bye()

    # if it is just one item and a directory
    # we navigate into it and start over inside of it
    if len(selected_items) == 1:
        item = selected_items[0]
        if Path(f'{current_folder}/{item}').is_dir():
            path = Path(f'{current_folder}/{item}')
            message = colored(f'You chose the directory: {item}', 'white')
            warning = colored('(iterating within the chosen folder...)', 'cyan')
            print(message)
            print(warning)
            return select_origin(f'{current_folder}/{item}')

        # return current_folder, selected_items

    # if there are several items we check none are a directory
    # if so, we return an error
    for item in selected_items:
        path = Path(f'{current_folder}/{item}')
        if path.is_dir():
            exception_msg = colored(
                'You cannot choose a folder when selecting several items',
                'red',
                attrs=['bold'],
            )
            raise Exception(exception_msg)

    return current_folder, selected_items


def progress(filename, size, sent):
    sys.stdout.write(
        "%s's progress: %.2f%%   \r" % (filename, float(sent) / float(size) * 100)
    )


def scp(origin_folder, origin_files, destination_folder):
    msg = colored(
        'You are about to copy the following files/folders into', 'yellow', attrs=['bold']
    )
    destination_msg = colored(destination_folder, 'red', attrs=['bold'])
    print(msg, destination_msg)
    for item in origin_files:
        msg = colored(f'- {item}', 'cyan', attrs=['bold'])
        print(msg)
    confirmation = input('Confirm to copy [y/n]:')

    if confirmation in ['y', 'Y', 'yes']:
        msg = colored('Copying...', 'green', attrs=['bold'])
        print(msg)

        with SSHClient() as ssh:
            ssh.load_system_host_keys()
            ssh.connect('totoro')

            with SCPClient(ssh.get_transport(), progress=progress) as scp:
                scp.put(
                    [f'{origin_folder}/{item}' for item in origin_files],
                    remote_path=destination_folder,
                )

        msg = colored('\nSetting permissions on copied files...', 'red', attrs=['bold'])
        print(msg)
        subprocess.run(
            [
                'ssh',
                'dvitto@totoro',
                f'chmod -R 755 "{destination_folder}"',
            ]
        )
        msg = colored('Checking files...', 'green', attrs=['bold'])
        print(msg)
        for item in origin_files:
            subprocess.run(
                [
                    'ssh',
                    'dvitto@totoro',
                    f'ls -al "{destination_folder}{item}"',
                ]
            )


def main():
    try:
        welcome()
        origin_folder, origin_items = select_origin()
        destination = select_destination()
        scp(origin_folder, origin_items, destination)
        bye()
    except Exception as err:
        print('\n', err, '\n')


if __name__ == "__main__":
    main()
