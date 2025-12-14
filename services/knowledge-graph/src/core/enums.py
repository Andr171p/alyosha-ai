from enum import StrEnum


class DocumentSource(StrEnum):
    """Источник документа (каким приложением он был сформирован)"""

    TXT = "txt"
    MS_WORD = "Microsoft Word"
    LIBRE_OFFICE = "LibreOffice"
    EXCEL = "Microsoft Excel"
    POWERPOINT = "Microsoft Powerpoint"
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    UNKNOWN = "unknown"


class DocumentCategory(StrEnum):
    """Категория контента к которой относится документ"""

    TEXT = "text"
    DOCUMENT = "document"
    TABLE = "table"
    PRESENTATION = "presentation"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    UNKNOWN = "unknown"
