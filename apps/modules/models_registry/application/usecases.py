from modules.shared_kernel.application import UnitOfWork

from ..domain import (
    AddAnyLLMToRegistryCommand,
    AddCommercialLLMToRegistryCommand,
    AnyLLM,
    CommercialLLM,
    OpenSourceLLM,
)
from .repository import RegistryRepository


def llm_factory(command: AddAnyLLMToRegistryCommand) -> AnyLLM:
    if isinstance(command, AddCommercialLLMToRegistryCommand):
        return CommercialLLM.create(command)
    return OpenSourceLLM.create(command)


class AddLLMToRegistryUseCase:
    def __init__(self, uow: UnitOfWork, repository: RegistryRepository) -> None:
        self._uow = uow
        self._repository = repository

    async def execute(self, command: AddAnyLLMToRegistryCommand) -> AnyLLM:
        async with self._uow.transactional() as uow:
            llm = llm_factory(command)
            await self._repository.create(llm)
            await uow.commit()
        return llm
