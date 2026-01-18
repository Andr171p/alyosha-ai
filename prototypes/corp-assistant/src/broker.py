import io
import logging
from collections.abc import Iterator

import magic
from aiogram import Bot
from aiogram.types import BufferedInputFile, Message
from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from pydub import AudioSegment
from pydub.utils import make_chunks

from .core import schemas
from .integrations import salute_speech
from .services.minutes import generate_minutes_of_meeting, render_document
from .settings import settings
from .utils import audio_mime_to_ext, current_datetime, progress_emojis

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


def split_audio_into_segments(
        audio_data: bytes, audio_format: str, segment_duration_ms: int = 60 * 20 * 1000
) -> Iterator[schemas.AudioSegment]:
    logger.info("Start split audio on segments...")
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format)
    chunks = make_chunks(audio, segment_duration_ms)
    chunks_count = len(chunks)
    logger.info("Created %s segments from audio", chunks_count)
    for i, chunk in enumerate(chunks):
        buffer = io.BytesIO()
        chunk.export(buffer, format="wav", bitrate="192k")
        logger.info("Export %s segment data to WAV format", i)
        chunk_data = buffer.getvalue()
        yield schemas.AudioSegment(
            index=i,
            segments_count=chunks_count,
            data=chunk_data,
            size=len(chunk_data),
            audio_format="wav",
            duration_ms=segment_duration_ms
        )


async def update_progress(
        bot: Bot, chat_id: int, percent: float, previous_message_id: int | None = None
) -> Message:
    text = f"""
    Расшифровываю аудио ...
    {progress_emojis(percent)}
    <b>{percent:.1f}%</b>
    """
    await bot.delete_message(chat_id=chat_id, message_id=previous_message_id)
    return await bot.send_message(chat_id=chat_id, text=text)


@broker.subscriber("minutes:draw_up")
async def process_minutes_task(task: schemas.MinutesTask, logger: Logger) -> None:
    from .bot import bot  # noqa: PLC0415

    bot_message = await bot.send_message(
        chat_id=task.user_id,
        text="Начинаю обработку аудио записи, это может занять от 5 до 15 минут ⏳..."
    )
    transcription_segments: list[str] = []
    for audio_file in task.audio_files:
        audio_data = await bot.download_file(audio_file, destination=io.BytesIO())
        mime_type = magic.Magic(mime=True).from_buffer(audio_data)
        for audio_segment in split_audio_into_segments(
                audio_data, audio_format=audio_mime_to_ext(mime_type)
        ):
            bot_message = await update_progress(
                bot=bot,
                chat_id=task.user_id,
                percent=audio_segment.index + 1 / audio_segment.segments_count,
                previous_message_id=bot_message.message_id
            )
            transcription = await salute_speech.recognize_async(
                audio_data=audio_segment.data,
                audio_encoding="PCM_S16LE",
                max_speakers=task.max_speakers,
            )
            transcription_segments.append(transcription)
    full_transcription = "\n".join(transcription_segments)
    await bot.delete_message(chat_id=task.user_id, message_id=bot_message.message_id)
    await bot.send_message(
        chat_id=task.user_id,
        text="Всё распознано! 🎤\nФормирую протокол совещания… ✍️\nЭто займёт ещё 30–90 секунд",
    )
    minutes_md = await generate_minutes_of_meeting(full_transcription)
    document_file = render_document(minutes_md, document_ext=task.document_ext)
    await bot.send_document(
        chat_id=task.user_id, document=BufferedInputFile(
            file=document_file,
            filename=f"Прокол_совещания_{current_datetime()}{task.document_ext}"
        ),
        caption="Готово! 🎉"
    )
