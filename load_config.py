import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

base_folder: str = os.getenv("LOCAL_BASE_FOLDER")
origin_folder: str = os.getenv("SERVER_ORIGIN_FOLDER")
series_folder: str = os.getenv("SERVER_SERIES_FOLDER")
comedy_folder: str = os.getenv("SERVER_COMEDY_FOLDER")
destination_base_folder: str = os.getenv("SERVER_DESTINATION_BASE_FOLDER")
server_name: str = os.getenv("SERVER_NAME")
server_user: str = os.getenv("SERVER_USER")
