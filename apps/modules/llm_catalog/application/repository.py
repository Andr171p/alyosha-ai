from abc import abstractmethod

from modules.shared_kernel.application import CRUDRepository, Pagination

from ..domain import AnyLLM
from .dto import LLMFilters


class CatalogRepository(CRUDRepository[AnyLLM]):
    @abstractmethod
    async def get_most_popular(self, pagination: Pagination) -> list[AnyLLM]: ...

    @abstractmethod
    async def search_by_filters(
            self, filters: LLMFilters, pagination: Pagination
    ) -> list[AnyLLM]: ...
