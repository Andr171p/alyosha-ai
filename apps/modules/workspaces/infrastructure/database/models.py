from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    StrNull,
    StrUnique,
    TextNull,
    UUIDField,
)


class MemberModel(Base):
    __tablename__ = "members"

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), unique=False)
    user_id: Mapped[UUIDField]
    role: Mapped[str]
    status: Mapped[str]
    invited_by: Mapped[StrNull]

    workspace: Mapped["WorkspaceModel"] = relationship(back_populates="members")

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="member_uq"),
    )


class InvitationModel(Base):
    __tablename__ = "invitations"

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), unique=False)
    email: Mapped[str]
    member_role: Mapped[str]
    token: Mapped[str]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str]

    workspace: Mapped["WorkspaceModel"] = relationship(back_populates="invitations")


class WorkspaceModel(Base):
    __tablename__ = "workspaces"

    owner_id: Mapped[UUIDField]
    space_type: Mapped[str]
    name: Mapped[str]
    slug: Mapped[StrUnique]
    organization_type: Mapped[str]
    organization_url: Mapped[StrNull]
    description: Mapped[TextNull]

    members: Mapped[list["MemberModel"]] = relationship(
        back_populates="workspace", lazy="selectin"
    )
    invitations: Mapped[list["InvitationModel"]] = relationship(back_populates="workspace")

    @hybrid_property
    def members_count(self) -> int:
        return len(self.members) if self.members else 0

    @members_count.expression
    def members_count(cls):
        return (
            select([func.count(MemberModel.id)])
            .where(MemberModel.workspace_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
            .label("members_count")
        )
