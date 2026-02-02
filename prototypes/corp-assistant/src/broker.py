import io
import logging
import time
from collections.abc import Iterator

from aiogram import Bot
from aiogram.types import BufferedInputFile, Message
from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydub import AudioSegment
from pydub.utils import make_chunks

from .core import schemas
from .integrations import salute_speech
from .settings import PROMPTS_DIR, settings
from .utils import current_datetime, md_to_pdf, progress_emojis

logger = logging.getLogger(__name__)

broker = RedisBroker(
    settings.redis.url,
    socket_timeout=120.0,
    socket_connect_timeout=15.0,
    socket_keepalive=True,
    retry_on_timeout=True,
    health_check_interval=15
)

app = FastStream(broker)

MEETING_MINUTES_PROMPT = (PROMPTS_DIR / "meeting_minutes_prompt.md").read_text(encoding="utf-8")


def split_audio_into_segments(
        audio_data: bytes, audio_format: str, segment_duration_ms: int = 20 * 60 * 1000
) -> Iterator[schemas.AudioSegment]:
    """Разделяет аудио файл на сегменты с заданной продолжительностью.

    :param audio_data: Байты аудио файла.
    :param audio_format: Формат аудио, например: 'wav', 'ogg', 'm4a'.
    :param segment_duration_ms: Продолжительность сегмента в миллисекундах.
    :returns: Объекты аудио сегментов.
    """

    logger.info("Start split audio on segments...")
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format)
    chunks = make_chunks(audio, segment_duration_ms)
    chunks_count = len(chunks)
    logger.info("Created %s segments from audio", chunks_count)
    for i, chunk in enumerate(chunks):
        buffer = io.BytesIO()
        chunk.export(buffer, format="mp3")
        logger.info("Export %s segment data to MP3 format", i + 1)
        chunk_data = buffer.getvalue()
        yield schemas.AudioSegment(
            index=i,
            segments_count=chunks_count,
            data=chunk_data,
            size=len(chunk_data),
            audio_format="mp3",
            duration_ms=segment_duration_ms
        )


async def update_progress(
        bot: Bot, chat_id: int, percent: float, prev_message_id: int | None = None
) -> Message:
    """Обновляет сообщение с прогрессом расшифровки аудио записи"""

    text = f"""
    Расшифровываю аудио ...
    {progress_emojis(percent)}
    <b>{percent:.1f}%</b>
    """
    await bot.delete_message(chat_id=chat_id, message_id=prev_message_id)
    return await bot.send_message(chat_id=chat_id, text=text)


async def generate_meeting_minutes(transcription: str) -> str:
    """Генерирует протокол совещания по его транскрибации.

    :param transcription: Транскрибация совещания.
    :returns: Составленный протокол в Markdown формате.
    """

    model = ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3,
    )
    prompt = ChatPromptTemplate.from_template(MEETING_MINUTES_PROMPT)
    chain = prompt | model | StrOutputParser()
    return await chain.ainvoke({"transcription": transcription})


@broker.subscriber("minutes:draw_up")
async def process_minutes_task(task: schemas.MinutesTask, logger: Logger) -> None:
    from .bot import bot  # noqa: PLC0415

    bot_message = await bot.send_message(
        chat_id=task.user_id,
        text="Скачиваю аудио файл 🔜 ..."
    )
    transcription_segments: list[str] = []
    start_time = time.time()
    file_buffer = await bot.download_file(task.audio_path, destination=io.BytesIO())
    audio_data = file_buffer.getbuffer().tobytes()
    logger.info(
        "Audio file `%s` downloaded from telegram, size %s mb, downloading time %s seconds",
        task.audio_path, round(len(audio_data) / 1_000_000, 2), round(time.time() - start_time, 2)
    )
    for audio_segment in split_audio_into_segments(audio_data, audio_format=task.audio_format):
        bot_message = await update_progress(
            bot=bot,
            chat_id=task.user_id,
            percent=audio_segment.index + 1 / audio_segment.segments_count * 100,
            prev_message_id=bot_message.message_id
        )
        logger.info(
            "Recognizing %s/%s segment of audio file `%s`",
            audio_segment.index + 1, audio_segment.segments_count, task.audio_path
        )
        transcription = await salute_speech.recognize_async(
            audio_data=audio_segment.data,
            audio_encoding="MP3",
            max_speakers=task.max_speakers,
        )
        transcription_segments.append(transcription)
    full_transcription = "\n".join(transcription_segments)
    await bot.delete_message(chat_id=task.user_id, message_id=bot_message.message_id)
    await bot.send_message(
        chat_id=task.user_id,
        text="Всё распознано! 🎤\nФормирую протокол совещания… ✍️\nЭто займёт ещё 30–90 секунд",
    )
    md_content = await generate_meeting_minutes(full_transcription)
    execution_time = time.time() - start_time
    logger.info("Minutes of meeting completed, it took %s seconds", round(execution_time, 2))
    md_content = md_content.replace("```", "").replace("markdown", "")
    pdf_file = md_to_pdf(md_content)
    await bot.send_document(
        chat_id=task.user_id, document=BufferedInputFile(
            file=pdf_file,
            filename=f"Прокол_совещания_{current_datetime()}.pdf"
        ),
        caption="Ваш протокол совещания готов! 🎉"
    )
