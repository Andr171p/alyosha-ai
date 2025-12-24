import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)

YANDEX_CLOUD_APIKEY = os.getenv("YANDEX_CLOUD_APIKEY")
YANDEX_CLOUD_FOLDER_ID = os.getenv("YANDEX_CLOUD_FOLDER_ID")
YANDEX_CLOUD_BASE_URL = "https://llm.api.cloud.yandex.net/v1"
SELECTED_MODEL = f"gpt://{YANDEX_CLOUD_FOLDER_ID}/yandexgpt/rc"  # YandexGPT Pro 5.1

yandexgpt_pro = ChatOpenAI(
    api_key=YANDEX_CLOUD_APIKEY,
    base_url=YANDEX_CLOUD_BASE_URL,
    model=SELECTED_MODEL,
    temperature=0.5,
)

# Текущий идентификатор пользователя
current_user_id = uuid4()

# Тестовая база данных рабочих пространств
workspaces_db: list[dict] = [
    {
        "user_id": current_user_id,
        "workspace": {
            ""
        }
    },
]

customers_db: list[dict] = [
    {
        "user_id": "Идентификатор пользователя",
        "customer_info": ["Полезная информация о клиенте полученная в ходе брифинга"]
    },
]
