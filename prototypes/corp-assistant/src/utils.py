import io
from datetime import datetime

from markdown_pdf import MarkdownPdf, Section
from markitdown import MarkItDown

from .settings import TIMEZONE


def current_datetime() -> datetime:
    """Получение текущего времени в выбранном часовом поясе"""

    return datetime.now(TIMEZONE)


def convert_document_to_md(data: bytes, extension: str) -> str:
    """Конвертирует контент документа (.pptx, .pdf, .docx, .xlsx) в Markdown текст.

    :param data: Байты исходного документа.
    :param extension: Расширение документа, например: .pdf, .docx, .xlsx
    :returns: Markdown текст.
    """

    md = MarkItDown()
    result = md.convert_stream(io.BytesIO(data), file_extension=extension)
    return result.text_content


def escape_md2(text: str) -> str:
    """Экранирует специальные символы для Markdown V2"""

    chars_to_escape = r"_[]()~`>#+-=|{}.!"
    for char in chars_to_escape:
        text = text.replace(char, f"\\{char}")
    return text


def progress_emojis(perc: float, width: int = 10) -> str:
    filled = round(width * perc / 100)
    return "🌕" * filled + "🌑" * (width - filled)


def md_to_pdf(md_content: str) -> bytes:
    """Формирует PDF файл по Markdown контенту"""

    pdf = MarkdownPdf()
    pdf.add_section(Section(md_content))
    buffer = io.BytesIO()
    pdf.save_bytes(buffer)
    return buffer.getvalue()
