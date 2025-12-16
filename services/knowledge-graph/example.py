import logging
from pathlib import Path

import openai
from markitdown import MarkItDown

from src.settings import settings

logging.basicConfig(level=logging.INFO)

YANDEX_CLOUD_FOLDER = settings.yandexcloud.folder_id
YANDEX_CLOUD_API_KEY = settings.yandexcloud.apikey

client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://llm.api.cloud.yandex.net/v1",
    project=YANDEX_CLOUD_FOLDER,
)

# selected_model = f"gpt://{YANDEX_CLOUD_FOLDER}/yandexgpt/rc"
selected_model = f"gpt://{YANDEX_CLOUD_FOLDER}/gemma-3-27b-it/latest"

docx_file = "НИР_Косов Андрей Сергеевич.docx"
pptx_file = "ДИО_Алёша_AI.pptx"

path = Path(pptx_file)

prompt = "Дай максимально детальное описание для изображения"

md = MarkItDown(llm_client=client, llm_model=selected_model, llm_prompt=prompt)
result = md.convert(path)
Path(f"{path.stem}.md").write_text(result.text_content, encoding="utf-8")
