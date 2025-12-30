from modules.shared_kernel.application import UnitOfWork

from ..domain import LLMCard
from .repository import CatalogRepository


class AddLLMToCatalogUseCase:
    def __init__(self, uow: UnitOfWork, repository: CatalogRepository) -> None:
        self._uow = uow
        self._repository = repository

    async def execute(self, command: ...) -> LLMCard:
        async with self._uow.transactional() as uow:
            await self._repository.create(...)
            await uow.commit()
        return ...
