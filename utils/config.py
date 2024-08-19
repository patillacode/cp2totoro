import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

environment = os.getenv("ENVIRONMENT")

base_folder: str = os.getenv("LOCAL_BASE_FOLDER")
origin_folder: str = os.getenv("SERVER_ORIGIN_FOLDER")
series_folder: str = os.getenv("SERVER_SERIES_FOLDER")
comedy_folder: str = os.getenv("SERVER_COMEDY_FOLDER")
destination_base_folder: str = os.getenv("SERVER_DESTINATION_BASE_FOLDER")
server_name: str = os.getenv("SERVER_NAME")
server_user: str = os.getenv("SERVER_USER")

telegram_personal_phone_number: str = os.getenv("TELEGRAM_PERSONAL_PHONE_NUMBER")
telegram_personal_nickname: str = os.getenv("TELEGRAM_PERSONAL_NICKNAME")
telegram_api_id: str = os.getenv("TELEGRAM_API_ID")
telegram_api_hash: str = os.getenv("TELEGRAM_API_HASH")
telegram_channel_name: str = (
    os.getenv("REAL_CHANNEL_NAME")
    if environment == "production"
    else os.getenv("TEST_CHANNEL_NAME")
)
omdb_api_key: str = os.getenv("OMDB_API_KEY")
