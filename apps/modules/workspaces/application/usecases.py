from modules.iam.domain.exceptions import PermissionDeniedError
from modules.shared_kernel.application import MessageBus, UnitOfWork
from modules.shared_kernel.application.exceptions import NotFoundError

from ..domain import CreateWorkspaceCommand, InviteMemberCommand, Workspace
from .dto import SentInvitation
from .repositories import WorkspaceRepository


class CreateWorkspaceUseCase:
    def __init__(
            self, uow: UnitOfWork, repository: WorkspaceRepository, message_bus: MessageBus
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._message_bus = message_bus

    async def execute(self, command: CreateWorkspaceCommand) -> Workspace:
        async with self._uow.transactional() as uow:
            workspace, owner = Workspace.create(command)
            await self._repository.create(workspace)
            await self._repository.add_member(owner)
            created_workspace = await self._repository.read(workspace.id)
            await uow.commit()
        for event in workspace.collect_events():
            await self._message_bus.send(event)
        return created_workspace


class InviteMemberUseCase:
    def __init__(
            self,
            uow: UnitOfWork, repository: WorkspaceRepository,
    ) -> None:
        self._uow = uow
        self._repository = repository

    async def execute(self, command: InviteMemberCommand) -> SentInvitation:
        async with self._uow.transactional() as uow:
            workspace = await self._repository.read(command.workspace_id)
            if workspace is None:
                raise NotFoundError(
                    f"Workspace {command.workspace_id} not found!",
                    entity_name="Workspace",
                    details={"workspace_id": command.workspace_id},
                )
            member = await self._repository.get_member(workspace.id, command.invited_by)
            if member is None:
                raise NotFoundError(
                    f"Inviter {command.invited_by} not found in workspace {command.workspace_id}!",
                    entity_name="Member",
                    details={"workspace_id": command.workspace_id, "user_id": command.invited_by},
                )
            if not member.can_invite():
                raise PermissionDeniedError(
                    f"Member {member.user_id} can't invite, required role `manager` or higher!",
                    details={
                        "user_id": command.invited_by,
                        "workspace_id": command.workspace_id,
                        "member_role": member.role,
                    },
                )
            invitation = workspace.invite_member(command)
            added_invitation = self._repository.add_invitation(invitation)
            await uow.commit()
        return SentInvitation.model_validate(added_invitation)
