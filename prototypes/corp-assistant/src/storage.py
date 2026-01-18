import io
import mimetypes

import magic

from .core.schemas import File


async def download_file(file_id: str) -> File:
    """Скачивает отправленный в Telegram бота файл.

    :param file_id: Идентификатор файла внутри чата.
    """

    from .bot import bot  # noqa: PLC0415

    file = await bot.get_file(file_id)
    file_buffer = await bot.download_file(file.file_path, destination=io.BytesIO())
    file_data = file_buffer.getbuffer().tobytes()
    mime_type = magic.Magic(mime=True).from_buffer(file_data)
    extension = mimetypes.guess_extension(mime_type, strict=True)
    return File(
        path=file.file_path,
        size=len(file_data),
        mime_type=mime_type,
        extension=extension,
        data=file_data
    )
