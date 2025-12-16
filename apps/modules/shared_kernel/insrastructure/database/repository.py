from typing import Any

from abc import abstractmethod
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application import Pagination
from ...application.exceptions import (
    ConflictError,
    CreationError,
    DeleteError,
    ReadingError,
    UpdateError,
)
from ...domain import Entity
from .base import Base


class DataMapper[EntityT: Entity, ModelT: Any]:
    entity_class: type[EntityT]
    model_class: type[ModelT]

    @classmethod
    @abstractmethod
    def model_to_entity(cls, model: ModelT) -> EntityT: ...

    @classmethod
    @abstractmethod
    def entity_to_model(cls, entity: EntityT) -> ModelT: ...


class SQLAlchemyRepository[EntityT: Entity, ModelT: Base]:
    entity: type[EntityT]
    model: type[ModelT]
    data_mapper: type[DataMapper[EntityT, ModelT]]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: EntityT) -> EntityT:
        try:
            model = self.data_mapper.entity_to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return self.data_mapper.model_to_entity(model)
        except IntegrityError as e:
            raise ConflictError(entity_name=self.entity.__name__, original_error=e) from e
        except SQLAlchemyError as e:
            raise CreationError(entity_name=self.entity.__name__, original_error=e) from e

    async def read(self, id: UUID) -> EntityT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.data_mapper.model_to_entity(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_id=id, entity_name=self.entity.__name__, original_error=e
            ) from e

    async def read_all(self, pagination: Pagination) -> list[EntityT]:
        try:
            stmt = (
                select(self.model)
                .order_by(self.model.created_at.desc())
                .offset(pagination.offset)
                .limit(pagination.limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.data_mapper.model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__name__,
                entity_id="*",
                details={"page": pagination.page, "limit": pagination.limit},
                original_error=e
            ) from e

    async def update(self, id: UUID, **kwargs) -> EntityT | None:  # noqa: A002
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**kwargs)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.data_mapper.model_to_entity(model) if model else None
        except IntegrityError as e:
            raise ConflictError(entity_name=self.entity.__name__, original_error=e) from e
        except SQLAlchemyError as e:
            raise UpdateError(
                entity_id=id, entity_name=self.entity.__name__, original_error=e
            ) from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DeleteError(
                entity_id=id, entity_name=self.entity.__name__, original_error=e
            ) from e
        else:
            return result.rowcount > 0
