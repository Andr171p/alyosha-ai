from typing import ClassVar

from uuid import UUID

from pydantic import EmailStr, HttpUrl

from modules.shared_kernel.domain import Event

from .value_objects import MemberRole, OrganizationType


class WorkspaceCreatedEvent(Event):
    event_type: ClassVar[str] = "workspace_created"

    workspace_id: UUID
    name: str
    organization_type: OrganizationType
    organization_url: HttpUrl | None
    description: str | None


class MemberInvitedEvent(Event):
    event_type: ClassVar[str] = "member_invited"

    workspace_id: UUID
    invitation_id: UUID
    email: EmailStr
    member_role: MemberRole
    token: str
