from typing import Self

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pydantic import EmailStr, HttpUrl, NonNegativeInt

from modules.iam.domain.exceptions import PermissionDeniedError
from modules.shared_kernel.domain import AggregateRoot, Entity, InvariantViolationError
from modules.shared_kernel.utils import current_datetime, generate_safe_string

from .commands import CreateWorkspaceCommand, InviteMemberCommand
from .events import MemberInvitedEvent, WorkspaceCreatedEvent
from .value_objects import (
    InvitationStatus,
    MemberRole,
    MemberStatus,
    OrganizationType,
    WorkspaceType,
)

INVITATION_EXPIRES_AT_DAYS = 7


class Member(Entity):
    """Участник рабочего пространства"""

    workspace_id: UUID
    user_id: UUID
    role: MemberRole
    status: MemberStatus
    invited_by: UUID | None = None

    @classmethod
    def create_owner(cls, workspace_id: UUID, user_id: UUID) -> Self:
        return cls(
            workspace_id=workspace_id,
            user_id=user_id,
            role=MemberRole.OWNER,
            status=MemberStatus.ACTIVE,
        )

    @property
    def is_owner(self) -> bool:
        """Является ли участник владельцем"""

        return self.role == MemberRole.OWNER

    def can_invite(self) -> bool:
        """Проверка может ли участник приглашать других участников"""

        return self.role in {MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER}

    def has_role(self, role: MemberRole) -> bool:
        return self.role == role

    def authorize(self) -> Self:
        if self.status != MemberStatus.ACTIVE:
            raise PermissionDeniedError(
                f"Member status is `{self.status.value}`!",
                details={
                    "workspace_id": self.workspace_id,
                    "user_id": self.user_id,
                    "role": self.role
                },
            )
        return self


class Invitation(Entity):
    """Приглашение пользователя в рабочее пространство"""

    workspace_id: UUID
    email: EmailStr
    member_role: MemberRole
    token: str
    expires_at: datetime
    status: InvitationStatus


class Workspace(AggregateRoot):
    """Рабочее пространство компании (создаётся админом).

    Attributes:
        owner_id: Идентификатор владельца области (ссылка на ID пользователя).
        space_type: Тип рабочего пространства (может быть 'private', 'public').
        name: Имя области.
        slug: Имя области отображаемое в URL.
        organization_type: Тип организации (обязательно поле).
        organization_url: URL адрес компании (адрес главного сайта).
        description: Описание предметной области.
        members_count: Количество участников.
    """

    owner_id: UUID
    space_type: WorkspaceType
    name: str
    slug: str
    organization_type: OrganizationType
    organization_url: HttpUrl | None = None
    description: str | None = None
    members_count: NonNegativeInt

    @classmethod
    def create(cls, command: CreateWorkspaceCommand) -> tuple[Self, Member]:
        """Фабричный метод для создания рабочего пространства"""

        workspace_id = uuid4()
        owner = Member.create_owner(workspace_id=workspace_id, user_id=command.user_id)
        workspace = cls(
            id=workspace_id,
            owner_id=command.user_id,
            space_type=command.space_type,
            name=command.name,
            slug=command.slug,
            organization_type=command.organization_type,
            organization_url=command.organization_url,
            description=command.description,
            members_count=1,
        )
        cls._register_event(workspace, WorkspaceCreatedEvent(
            workspace_id=workspace.id,
            name=workspace.name,
            organization_type=workspace.organization_type,
            organization_url=workspace.organization_url,
            description=workspace.description,
        ))
        return workspace, owner

    def invite_member(self, command: InviteMemberCommand) -> Invitation:
        if self.id != command.workspace_id:
            raise InvariantViolationError(
                "Workspace IDs in command do not match!",
                entity_name=self.__class__.__name__,
                details={"workspace_id": self.id, "command_workspace_id": command.workspace_id},
            )
        invitation = Invitation(
            workspace_id=command.workspace_id,
            email=command.email,
            member_role=command.member_role,
            token=generate_safe_string(),
            expires_at=current_datetime() + timedelta(days=INVITATION_EXPIRES_AT_DAYS),
            status=InvitationStatus.PENDING,
        )
        self._register_event(MemberInvitedEvent(
            workspace_id=self.id,
            invitation_id=invitation.id,
            email=invitation.email,
            member_role=invitation.member_role,
            token=invitation.token
        ))
        return invitation
