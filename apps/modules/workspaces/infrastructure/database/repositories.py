from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from modules.shared_kernel.application import Pagination
from modules.shared_kernel.application.exceptions import ConflictError, CreationError, ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import WorkspaceRepository
from ...domain import Invitation, Member, OrganizationType, Workspace, WorkspaceType
from .models import InvitationModel, MemberModel, WorkspaceModel


class WorkspaceDataMapper(DataMapper[Workspace, WorkspaceModel]):
    @classmethod
    def model_to_entity(cls, model: WorkspaceModel) -> Workspace:
        return Workspace(
            id=model.id,
            space_type=WorkspaceType(model.space_type),
            owner_id=model.owner_id,
            name=model.name,
            slug=model.slug,
            organization_type=OrganizationType(model.organization_type),
            organization_url=model.organization_url,
            description=model.description,
            members_count=model.members_count,
            created_at=model.created_at,
        )

    @classmethod
    def entity_to_model(cls, entity: Workspace) -> WorkspaceModel:
        return WorkspaceModel(
            id=entity.id,
            owner_id=entity.owner_id,
            space_type=entity.space_type,
            name=entity.name,
            slug=entity.slug,
            organization_type=entity.organization_type,
            organization_url=str(entity.organization_url),
            description=entity.description,
            created_at=entity.created_at,
        )


class MemberDataMapper(DataMapper[Member, MemberModel]):
    @classmethod
    def model_to_entity(cls, model: MemberModel) -> Member:
        return Member.model_validate(model)

    @classmethod
    def entity_to_model(cls, entity: Member) -> MemberModel:
        return MemberModel(**entity.model_dump())


class InvitationDataMapper(DataMapper[Invitation, InvitationModel]):
    @classmethod
    def model_to_entity(cls, model: InvitationModel) -> Invitation:
        return Invitation.model_validate(model)

    @classmethod
    def entity_to_model(cls, entity: Invitation) -> InvitationModel:
        return InvitationModel(**entity.model_dump())


class SQLAlchemyWorkspaceRepository(
    SQLAlchemyRepository[Workspace, WorkspaceModel], WorkspaceRepository
):
    entity = Workspace
    model = WorkspaceModel
    data_mapper = WorkspaceDataMapper

    async def get_by_owner(self, owner_id: UUID) -> list[Workspace]:
        try:
            stmt = select(self.model).where(self.model.owner_id == owner_id)
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.data_mapper.model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__class__.__name__,
                entity_id=owner_id,
                details={"owner_id": owner_id},
                original_error=e
            ) from e

    async def get_member(self, workspace_id: UUID, user_id: UUID) -> Member | None:
        try:
            stmt = (
                select(MemberModel)
                .where(
                    (MemberModel.workspace_id == workspace_id) &
                    (MemberModel.user_id == user_id)
                )
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return MemberDataMapper.model_to_entity(model) if model is not None else None
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name="Member",
                entity_id=user_id,
                details={"workspace_id": workspace_id, "user_id": user_id},
                original_error=e
            ) from e

    async def get_members(self, workspace_id: UUID, pagination: Pagination) -> list[Member]:
        try:
            stmt = (
                select(MemberModel)
                .where(MemberModel.workspace_id == workspace_id)
                .order_by(MemberModel.created_at.desc())
                .offset(pagination.offset)
                .limit(pagination.limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [MemberDataMapper.model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name="Member",
                entity_id="*",
                details={
                    "workspace_id": workspace_id,
                    "page": pagination.page,
                    "limit": pagination.limit,
                },
                original_error=e
            ) from e

    async def add_member(self, member: Member) -> Member:
        try:
            model = MemberDataMapper.entity_to_model(member)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return MemberDataMapper.model_to_entity(model)
        except IntegrityError as e:
            raise ConflictError(entity_name="Member", original_error=e) from e
        except SQLAlchemyError as e:
            raise CreationError(entity_name="Member", original_error=e) from e

    async def add_invitation(self, invitation: Invitation) -> Invitation:
        try:
            model = InvitationDataMapper.entity_to_model(invitation)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return InvitationDataMapper.model_to_entity(model)
        except IntegrityError as e:
            raise ConflictError(entity_name="Invitation", original_error=e) from e
        except SQLAlchemyError as e:
            raise CreationError(entity_name="Invitation", original_error=e) from e
