from typing import Annotated

from collections.abc import AsyncIterable

from fastapi import APIRouter, File, Query, UploadFile, status
from pydantic import PositiveInt

from src.core import Document
from src.pipeline.loader import upload_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    path="/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=Document,
    summary="Загрузка документа по частям"
)
async def upload(
        chunk_size: Annotated[PositiveInt, Query(ge=0, le=65536)],
        file: Annotated[UploadFile, File(...)]
) -> Document:
    filename = file.filename

    async def content_generator() -> AsyncIterable[bytes]:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    return await upload_document(filename, content_generator())
