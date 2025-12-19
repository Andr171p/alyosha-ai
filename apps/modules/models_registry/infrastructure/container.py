from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared_kernel.application import UnitOfWork

from ..application import AddLLMToRegistryUseCase, RegistryRepository
from .database import SQLAlchemyRegistryRepository


class ModelsRegistryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_registry_repo(self, session: AsyncSession) -> RegistryRepository:  # noqa: PLR6301
        return SQLAlchemyRegistryRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_llm_to_registry_addition_usecase(  # noqa: PLR6301
            self, uow: UnitOfWork, repository: RegistryRepository
    ) -> AddLLMToRegistryUseCase:
        return AddLLMToRegistryUseCase(uow=uow, repository=repository)
