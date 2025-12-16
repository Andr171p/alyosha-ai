from abc import abstractmethod
from uuid import UUID

from modules.shared_kernel.application import CRUDRepository, Pagination

from ..domain import Invitation, Member, Workspace


class WorkspaceRepository(CRUDRepository[Workspace]):
    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> list[Workspace]:
        """Получение рабочих пространств по user_id"""

    @abstractmethod
    async def get_member(self, workspace_id: UUID, user_id: UUID) -> Member | None:
        """Получить участника"""

    @abstractmethod
    async def get_members(self, workspace_id: UUID, pagination: Pagination) -> list[Member]:
        """Получение всех участников в рабочем пространстве"""

    @abstractmethod
    async def add_member(self, member: Member) -> Member:
        """Добавление участника в рабочее пространство"""

    @abstractmethod
    async def add_invitation(self, invitation: Invitation) -> Invitation: ...


class InvitationRepository(CRUDRepository[Invitation]):
    @abstractmethod
    async def get_by_token(self, token: str) -> Invitation: ...
