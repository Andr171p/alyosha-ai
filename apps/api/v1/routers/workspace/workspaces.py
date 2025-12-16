from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from api.dependencies import (
    ManagerOrHigherRequiredDep,
    PaginationDep,
    require_manager_or_higher_dep,
)
from modules.iam.infrastructure.fastapi import CurrentUserDep
from modules.workspaces.application import CreateWorkspaceUseCase, WorkspaceRepository
from modules.workspaces.application.dto import SentInvitation, WorkspaceCreate
from modules.workspaces.domain import CreateWorkspaceCommand, Member, Workspace

router = APIRouter(prefix="/workspaces", tags=["Workspaces"], route_class=DishkaRoute)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=list[Workspace],
    summary="Получить мои рабочие области",
)
async def get_my_workspaces(
        current_user: CurrentUserDep, repository: FromDishka[WorkspaceRepository]
) -> list[Workspace]:
    return await repository.get_by_owner(current_user.user_id)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Workspace,
    summary="Создание рабочей области",
)
async def create_workspace(
        current_user: CurrentUserDep,
        body: WorkspaceCreate,
        usecase: FromDishka[CreateWorkspaceUseCase]
) -> Workspace:
    command = CreateWorkspaceCommand.model_validate({
        "user_id": current_user.user_id, **body.model_dump()
    })
    return await usecase.execute(command)


@router.get(
    path="/{workspace_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=list[Member],
    summary="Получить список участников",
    dependencies=[Depends(require_manager_or_higher_dep)]
)
async def get_members(
        workspace_id: UUID,
        pagination: PaginationDep,
        repository: FromDishka[WorkspaceRepository]
) -> list[Member]:
    return await repository.get_members(workspace_id, pagination)


@router.get(
    path="/{workspace_id}/members/{member_id}",
    status_code=status.HTTP_200_OK,
    response_model=Member,
    summary="Получить конкретного участника",
)
async def get_member(
        workspace_id: UUID, member_id: UUID, repository: FromDishka[WorkspaceRepository]
) -> Member:
    return await repository.get_member(workspace_id, member_id)


@router.post(
    path="/{workspace_id}/invitations",
    status_code=status.HTTP_201_CREATED,
    response_model=SentInvitation,
    summary="Приглашает участника в рабочую область",
)
async def invite_to_workspace(
        manager: ManagerOrHigherRequiredDep,
) -> SentInvitation: ...


'''
@router.post(
    path="/{workspace_id}/invitations/accept/{token}",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Принять приглашение",
)
async def accept_invitation() -> ...: ...
'''
