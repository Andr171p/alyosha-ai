import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..core import schemas
from ..core.schemas import DocumentExt
from ..settings import PROMPTS_DIR, settings
from ..utils import md_to_pdf

logger = logging.getLogger(__name__)

SUPPORTED_AUDIO_FORMATS = {"wav", "mp3", "m4a", "ogg", "flac"}


async def create_task(
        user_id: int,
        file_ids: list[str],
        max_speakers: int = 10,
        document_ext: DocumentExt = ".pdf",
) -> None:
    from ..bot import bot  # noqa: PLC0415
    from ..broker import broker  # noqa: PLC0415

    audio_files: list[str] = []
    for file_id in file_ids:
        file = await bot.get_file(file_id)
        file_format = file.file_path.split(".")[-1]
        if file_format not in SUPPORTED_AUDIO_FORMATS:
            logger.warning("Not supported audio format: %s!", file_format)
            continue
        audio_files.append(file.file_path)
    task = schemas.MinutesTask(
        audio_files=audio_files,
        user_id=user_id,
        max_speakers=max_speakers,
        document_ext=document_ext
    )
    await broker.publish(task, channel="minutes:draw_up")


async def generate_minutes_of_meeting(transcription: str) -> str:
    model = ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3,
    )
    prompt = ChatPromptTemplate.from_template(
        (PROMPTS_DIR / "minutes_of_meeting_prompt.md").read_text(encoding="utf-8")
    )
    chain = prompt | model | StrOutputParser()
    return await chain.ainvoke({"transcription": transcription})


def render_document(md_text: str, document_ext: DocumentExt) -> bytes:
    match document_ext:
        case "docx":
            return ...
        case "pdf":
            return md_to_pdf(md_text)
        case _:
            return ...
