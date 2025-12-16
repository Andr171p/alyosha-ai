from typing import Final

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
WORKDIR = BASE_DIR / ".workflow"

load_dotenv(ENV_PATH)


class YandexCloudSettings(BaseSettings):
    apikey: str = "<APIKEY>"
    folder_id: str = "<FOLDER_ID>"

    model_config = SettingsConfigDict(env_prefix="YANDEX_CLOUD_")


class Settings(BaseSettings):
    yandexcloud: YandexCloudSettings = YandexCloudSettings()


settings: Final[Settings] = Settings()
