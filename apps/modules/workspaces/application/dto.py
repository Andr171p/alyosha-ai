from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from modules.shared_kernel.application import DTO

from ..domain import InvitationStatus, MemberRole, OrganizationType, WorkspaceType


class WorkspaceCreate(DTO):
    space_type: WorkspaceType = Field(
        default=WorkspaceType.PRIVATE, description="Тип рабочего пространства"
    )
    name: str = Field(..., description="Название области")
    slug: str = Field(..., description="Уникальная строка для URL")
    organization_type: OrganizationType = Field(..., description="Тип организации")
    organization_url: str | None = Field(default=None, description="URL сайта организации")
    description: str | None = Field(default=None, description="Описание деятельности организации")
    use_ai_consultant: bool = Field(
        default=True, description="Использовать ли AI консультанта для работы с workspace"
    )


class SentInvitation(DTO):
    """Отправленное приглашение"""

    workspace_id: UUID
    email: EmailStr
    member_role: MemberRole
    expires_at: datetime
    status: InvitationStatus
