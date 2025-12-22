from typing import Annotated, TypeVar

from pydantic import Field, NonNegativeInt, PositiveInt

from modules.shared_kernel.domain import Entity, ValueObject

EntityT = TypeVar("EntityT", bound=Entity)
Limit = Annotated[NonNegativeInt, Field(ge=1, le=100)]


class Pagination(ValueObject):
    """Пагинация"""

    page: PositiveInt
    limit: Limit

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResult(ValueObject):
    """Результат запроса пагинации"""

    items: list[EntityT]
    total_count: NonNegativeInt
    page: PositiveInt
    limit: Limit
    total_pages: NonNegativeInt


class Filter(ValueObject):
    ...


class QueryOptions(ValueObject):
    ...
