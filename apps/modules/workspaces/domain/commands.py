from uuid import UUID

from pydantic import EmailStr, HttpUrl

from modules.shared_kernel.domain import Command

from .value_objects import MemberRole, OrganizationType, WorkspaceType


class CreateWorkspaceCommand(Command):
    """Команда для создания рабочей области"""

    user_id: UUID
    space_type: WorkspaceType
    name: str
    slug: str
    description: str | None = None
    organization_type: OrganizationType
    organization_url: HttpUrl | None = None


class InviteMemberCommand(Command):
    """Команда для приглашения участника в рабочее пространство"""

    workspace_id: UUID
    invited_by: UUID
    email: EmailStr
    member_role: MemberRole
