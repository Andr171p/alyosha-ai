from abc import abstractmethod

from modules.shared_kernel.application import CRUDRepository, Pagination

from ..domain import LLMCard
from .dto import LLMFilters


class CatalogRepository(CRUDRepository[LLMCard]):
    @abstractmethod
    async def get_most_popular(self, pagination: Pagination) -> list[LLMCard]: ...

    @abstractmethod
    async def search_by_filters(
            self, filters: LLMFilters, pagination: Pagination
    ) -> list[LLMCard]: ...
