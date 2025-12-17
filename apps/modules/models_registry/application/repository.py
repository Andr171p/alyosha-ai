from abc import abstractmethod

from modules.shared_kernel.application import CRUDRepository

from ..domain import ModelEntry


class RegistryRepository(CRUDRepository[ModelEntry]):
    @abstractmethod
    async def sort_by_usage_count(self) -> list[ModelEntry]: ...
