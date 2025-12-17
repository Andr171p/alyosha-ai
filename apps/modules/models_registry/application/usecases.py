from modules.shared_kernel.application import UnitOfWork

from ..domain import CreateEntryCommand, ModelEntry
from .repository import RegistryRepository


class CreateEntryUseCase:
    def __init__(self, uow: UnitOfWork, repository: RegistryRepository) -> None:
        self._uow = uow
        self._repository = repository

    async def execute(self, command: CreateEntryCommand) -> ModelEntry:
        async with self._uow.transactional() as uow:
            model_entry = ModelEntry.create(command)
            await self._repository.create(model_entry)
            await uow.commit()
        return model_entry
