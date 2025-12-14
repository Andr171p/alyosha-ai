from pathlib import Path
from uuid import uuid4

from ..core import DocumentCategory, DocumentSource

_DOCUMENT_TYPES_MAP = {
    # Текстовые файлы
    ".txt": (DocumentCategory.TEXT, DocumentSource.TXT),
    ".md": (DocumentCategory.TEXT, DocumentSource.TXT),
    # Документы
    ".pdf": (DocumentCategory.DOCUMENT, DocumentSource.PDF),
    ".doc": (DocumentCategory.DOCUMENT, DocumentSource.MS_WORD),
    ".docx": (DocumentCategory.DOCUMENT, DocumentSource.MS_WORD),
    ".odt": (DocumentCategory.DOCUMENT, DocumentSource.LIBRE_OFFICE),
    ".rtf": (DocumentCategory.DOCUMENT, DocumentSource.UNKNOWN),
    # Таблицы
    ".csv": (DocumentCategory.TABLE, DocumentSource.TXT),
    ".xlsx": (DocumentCategory.TABLE, DocumentSource.EXCEL),
    ".xls": (DocumentCategory.TABLE, DocumentSource.EXCEL),
    ".ods": (DocumentCategory.TABLE, DocumentSource.LIBRE_OFFICE),
    # Презентации
    ".ppt": (DocumentCategory.PRESENTATION, DocumentSource.POWERPOINT),
    ".pptx": (DocumentCategory.PRESENTATION, DocumentSource.POWERPOINT),
    ".odp": (DocumentCategory.PRESENTATION, DocumentSource.LIBRE_OFFICE),
    # Изображения
    ".jpg": (DocumentCategory.IMAGE, DocumentSource.IMAGE),
    ".jpeg": (DocumentCategory.IMAGE, DocumentSource.IMAGE),
    ".png": (DocumentCategory.IMAGE, DocumentSource.IMAGE),
    ".gif": (DocumentCategory.IMAGE, DocumentSource.IMAGE),
    ".bmp": (DocumentCategory.IMAGE, DocumentSource.IMAGE),
    ".svg": (DocumentCategory.IMAGE, DocumentSource.IMAGE),
    # Аудио
    ".mp3": (DocumentCategory.AUDIO, DocumentSource.AUDIO),
    ".wav": (DocumentCategory.AUDIO, DocumentSource.AUDIO),
    ".ogg": (DocumentCategory.AUDIO, DocumentSource.AUDIO),
    ".flac": (DocumentCategory.AUDIO, DocumentSource.AUDIO),
    # Видео
    ".mp4": (DocumentCategory.VIDEO, DocumentSource.VIDEO),
    ".avi": (DocumentCategory.VIDEO, DocumentSource.VIDEO),
    ".mov": (DocumentCategory.VIDEO, DocumentSource.VIDEO),
    ".mkv": (DocumentCategory.VIDEO, DocumentSource.VIDEO),
    # Архивы
    ".zip": (DocumentCategory.ARCHIVE, DocumentSource.UNKNOWN),
    ".rar": (DocumentCategory.ARCHIVE, DocumentSource.UNKNOWN),
    ".tar": (DocumentCategory.ARCHIVE, DocumentSource.UNKNOWN),
    ".gz": (DocumentCategory.ARCHIVE, DocumentSource.UNKNOWN),
    # Код
    ".py": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
    ".js": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
    ".java": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
    ".cpp": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
    ".html": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
    ".css": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
    ".json": (DocumentCategory.CODE, DocumentSource.UNKNOWN),
}


def detect_document_types(path: Path) -> tuple[DocumentCategory, DocumentSource] | None:
    """Определение категории и источника документа по его пути"""

    return _DOCUMENT_TYPES_MAP.get(path.suffix)


def generate_unique_slug(filename: str) -> str:
    """Генерация уникального файлового псевдонима"""

    from .common import current_datetime  # noqa: PLC0415

    return (
        f"{Path(filename).stem}_{current_datetime().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    )
