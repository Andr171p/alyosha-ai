from typing import Annotated

from uuid import UUID

from fastapi import Path

from modules.iam.domain.exceptions import PermissionDeniedError
from modules.iam.infrastructure.fastapi import CurrentUserDep

from ...application import WorkspaceRepository
from ...domain import Member

WorkspaceIdPath = Annotated[UUID, Path(..., description="ID рабочего пространства")]


async def get_current_member(
        workspace_id: WorkspaceIdPath,
        current_user: CurrentUserDep,
        workspace_repository: WorkspaceRepository,
) -> Member:
    """Получение текущего участника (тот который делает запрос)"""

    member = await workspace_repository.get_member(workspace_id, current_user.user_id)
    if not member:
        raise PermissionDeniedError(
            f"User is not a member of workspace {workspace_id}",
            details={"workspace_id": workspace_id, "user_id": current_user.user_id},
        )
    return member.authorize()
