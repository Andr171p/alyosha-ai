import logging
from collections.abc import AsyncIterable

import aiofiles

from ..core import Document, DocumentWorkflowStructure
from ..utils.files import detect_document_types

logger = logging.getLogger(__name__)


async def upload_document(filename: str, content: AsyncIterable[bytes]) -> Document:
    """Загрузка документа в рабочее пространство для дальнейшего анализа.

    :param filename: Оригинальное имя файла.
    :param content: Бинарные данные файла.
    :returns: Метаданные документа.
    """

    logger.info("Start uploading `%s` file", filename)
    workflow_structure = DocumentWorkflowStructure.from_filename(filename)
    logger.info("Workflow structure created, workdir - `%s`", workflow_structure.root)
    async with aiofiles.open(workflow_structure.input_file, mode="wb") as file:
        async for chunk in content:
            await file.write(chunk)
    category, source = detect_document_types(workflow_structure.input_file)
    logger.info("Document uploaded successfully")
    return Document(
        path=workflow_structure.input_file,
        filename=filename,
        slug=workflow_structure.slug,
        size=workflow_structure.input_file.stat().st_size,
        category=category,
        source=source,
    )
