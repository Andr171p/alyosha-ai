from typing import Any, Self

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, FilePath, PositiveInt, computed_field

from ..settings import WORKDIR
from ..utils.common import current_datetime
from ..utils.files import generate_unique_slug
from .enums import DocumentCategory, DocumentSource


class DocumentWorkflowStructure(BaseModel):
    """Структура рабочего пространства для документа"""

    root: Path
    input_file: Path
    metadata_file: Path

    @computed_field(description="Директория с медиа вложениями внутри документа")
    def attachments_dir(self) -> Path:
        path = self.root / "attachments"
        path.mkdir(exist_ok=True)
        return path

    @property
    def slug(self) -> str:
        """Уникальный идентификатор (псевдоним) рабочей директории"""

        return self.root.name

    @classmethod
    def from_filename(cls, filename: str) -> Self:
        """Создание рабочей директории по имени файла"""

        path = Path(filename)
        slug = generate_unique_slug(filename)
        root = WORKDIR / slug
        root.mkdir(parents=True, exist_ok=True)
        return cls(
            root=root,
            input_file=root / f"input{path.suffix}",
            metadata_file=root / "metadata.json",
        )

    @classmethod
    def from_existing(cls, slug: str) -> Self:
        root = WORKDIR / slug
        input_file = next(
            (path for path in Path(root).glob("input.*") if path.is_file()),
            None
        )
        if input_file is None:
            raise ValueError(f"Document not uploaded in directory {root}!")
        return cls(
            root=root,
            input_file=input_file,
            metadata_file=root / "metadata.json",
        )


class Document(BaseModel):
    """Документ загруженный в систему пользователем"""

    filename: str
    path: FilePath
    slug: str
    size: PositiveInt
    category: DocumentCategory
    source: DocumentSource
    metadata: dict[str, Any] = Field(default_factory=dict)
    uploaded_at: datetime = Field(default_factory=current_datetime)

    @property
    def workflow_structure(self) -> DocumentWorkflowStructure:
        return DocumentWorkflowStructure.from_existing(self.slug)
