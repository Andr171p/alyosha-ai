import io
import subprocess  # noqa: S404
from datetime import datetime
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section
from markitdown import MarkItDown

from .core.exceptions import FileDoesNotExistError
from .settings import TIMEZONE


def current_datetime() -> datetime:
    """Получение текущего времени в выбранном часовом поясе"""

    return datetime.now(TIMEZONE)


def convert_document_to_markdown(doc_path: str) -> str:
    """Конвертирует документы в Markdown текст"""

    if not Path(doc_path).exists():
        raise FileDoesNotExistError(f"`{doc_path} does not exist!`")
    md = MarkItDown()
    result = md.convert(doc_path)
    return result.text_content


def create_docx_file_from_markdown(md_text: str) -> bytes:
    """Создаёт docx документ по Markdown тексту.

    :param md_text: Markdown текст.
    :returns: Байты docx документа.
    """

    try:
        result = subprocess.run(  # noqa: S603
            ("pandoc", "-f", "markdown", "-t", "docx"),
            input=md_text.encode("utf-8"),
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "Pandoc not found in system. Install: https://pandoc.org/installing.html"
        )from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Pandoc error: \n{e.stderr.decode('utf-8', errors='replace')}"
        ) from e
    else:
        return result.stdout


def create_pdf_file_from_markdown(md_text: str) -> bytes:
    """Создаёт PDF документ по Markdown тексту.

    :param md_text: Markdown текст.
    :returns: Байты PDF документа.
    """

    pdf = MarkdownPdf()
    pdf.meta["title"] = "Document"
    pdf.add_section(Section(md_text))
    buffer = io.BytesIO()
    pdf.save_bytes(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def create_md_file_from_markdown(md_text: str) -> bytes:
    """Создаёт MD файл по Markdown тексту.

    :param md_text: Markdown текст.
    :returns: Байты Markdown файла.
    """

    with io.BytesIO() as buffer:
        buffer.write(md_text.encode("utf-8"))
        buffer.seek(0)
    return buffer.read()


def escape_md2(text: str) -> str:
    """Экранирует специальные символы для Markdown V2"""

    chars_to_escape = r"_[]()~`>#+-=|{}.!"
    for char in chars_to_escape:
        text = text.replace(char, f"\\{char}")
    return text
