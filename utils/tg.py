import requests

from telethon import TelegramClient
from termcolor import colored

from utils.config import (
    omdb_api_key,
    telegram_api_hash,
    telegram_api_id,
    telegram_channel_name,
    telegram_personal_nickname,
    telegram_personal_phone_number,
)

telegram_telethon_client = TelegramClient(
    telegram_personal_nickname, telegram_api_id, telegram_api_hash
)


async def test_telegram_client():
    await telegram_telethon_client.start(phone=telegram_personal_phone_number)
    async with telegram_telethon_client:
        await telegram_telethon_client.send_message(telegram_channel_name, "proident!")


def ask_user_to_send_message():
    msg = colored(
        f'\nDo you want to send a message to "{telegram_channel_name}" to inform '
        "that you added new content to Totoro? (y/N): ",
        "green",
        attrs=["bold"],
    )
    return input(msg).lower() == "y"


def download_poster(url, file_path):
    try:
        response = requests.get(url)
        # Check if the request was successful
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(colored("Poster downloaded successfully!", "green", attrs=["dark"]))
        return True

    except requests.exceptions.RequestException as err:
        msg: str = colored(
            f"An error occurred while downloading the poster: {err}",
            "red",
            attrs=["bold"],
        )
        error_msg = colored(msg, "red", attrs=["dark"])
        print(msg)
        print(error_msg)
        return False


def check_it_is_the_right_movie(imdb_link):
    msg = colored(
        "check the following imdb link to make sure it's the right media: ",
        "yellow",
        attrs=["dark"],
    )
    print(msg, end="")

    msg = colored(imdb_link, "green", attrs=["bold"])
    print(msg)

    msg: str = colored(
        "\nIs this the media you are looking for? (y/n): ", "yellow", attrs=["bold"]
    )
    return input(msg).lower() == "y"


def build_telegram_message():
    msg: str = colored(
        "\nLet's get the information about the media you want to send the message about:",
        "yellow",
        attrs=["bold"],
    )
    print(msg)
    movie_name = input(colored("Name: ", "yellow", attrs=["bold"]))
    movie_year = input(colored("Year: ", "yellow", attrs=["bold"]))
    if not movie_name or not movie_year:
        msg: str = colored(
            "\nMovie name and year are required to send the message. Try again.",
            "red",
            attrs=["bold"],
        )
        print(msg)
        build_telegram_message()

    api_url = (
        f"https://www.omdbapi.com/?apikey={omdb_api_key}"
        f"&t={movie_name}"
        f"&y={movie_year}"
        "&plot=short&r=json"
    )

    try:
        movie_data = requests.get(api_url).json()

    except Exception as err:
        msg: str = colored(
            f"An error occurred while fetching the movie data: {err}",
            "red",
            attrs=["bold"],
        )
        print(msg)
        return None, None

    title = movie_data["Title"]
    year = movie_data["Year"]
    plot = movie_data["Plot"]
    poster = movie_data["Poster"]
    poster_path = f"/tmp/{title}.jpg"
    download_poster(poster, poster_path)

    imdb_link = f"https://www.imdb.com/title/{movie_data['imdbID']}/"
    imdb_rating = movie_data["imdbRating"]

    try:
        rotten_tomatoes_rating = movie_data["Ratings"][1]["Value"]
        rotten_tomatoes_message = (
            f"🍅 **Valoración en Rotten Tomatoes:** {rotten_tomatoes_rating}"
        )
    except IndexError:
        rotten_tomatoes_rating = None

    genre = movie_data["Genre"]

    if not check_it_is_the_right_movie(imdb_link):
        msg: str = colored(
            "The content data fetched is not the one you are looking for.",
            "red",
            attrs=["bold"],
        )
        print(msg)

        msg = colored("You're gonna need to this one manually.", "red", attrs=["dark"])
        print(msg)

        return None, None

    message = f"""
**{title}**

¡Nuevo contenido ya disponible en el servidor!

__{plot}__

🎬 **Género:** {genre}
📅 **Año:** {year}
⭐️ **Valoración en IMDB:** {imdb_rating}
{rotten_tomatoes_message if rotten_tomatoes_rating else ""}
🔗 [IMDB]({imdb_link})
"""

    return message, poster_path


async def send_message_to_telegram_channel():
    if ask_user_to_send_message():
        message, poster_path = build_telegram_message()
        if message:
            print(
                colored(
                    "Sending message to Telegram channel...", "green", attrs=["dark"]
                ),
                end=" ",
            )
            await telegram_telethon_client.start(phone=telegram_personal_phone_number)
            async with telegram_telethon_client:
                await telegram_telethon_client.send_file(
                    telegram_channel_name, poster_path, caption=message
                )
                icon: str = colored("􀆅", "green", attrs=["bold"])
                print(icon)
    else:
        msg: str = colored(
            "Ok, not sending any message to the Telegram channel.",
            "yellow",
            attrs=["bold"],
        )
        print(msg)
