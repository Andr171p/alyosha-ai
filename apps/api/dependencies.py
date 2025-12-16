from typing import Annotated

from collections.abc import Callable

from dishka import Scope
from fastapi import Depends, Query
from pydantic import PositiveInt

from modules.iam.domain.exceptions import PermissionDeniedError
from modules.iam.infrastructure.fastapi import CurrentUserDep
from modules.shared_kernel.application import Pagination
from modules.workspaces.application import WorkspaceRepository
from modules.workspaces.domain import Member, MemberRole
from modules.workspaces.infrastructure.fastapi import WorkspaceIdPath, get_current_member

from .container import container


def _get_pagination(
        page: Annotated[PositiveInt, Query(..., description="Номер страницы")] = 1,
        limit: Annotated[
            PositiveInt, Query(..., description="Количество элементов на странице")
        ] = 20,
) -> Pagination:
    return Pagination(page=page, limit=limit)


PaginationDep = Annotated[Pagination, Depends(_get_pagination)]


async def _get_current_member(
        workspace_id: WorkspaceIdPath, current_user: CurrentUserDep,
) -> Member:
    async with container(scope=Scope.REQUEST) as request_container:
        workspace_repository = await request_container.get(WorkspaceRepository)
        return await get_current_member(
            workspace_id=workspace_id,
            current_user=current_user,
            workspace_repository=workspace_repository
        )


# Зависимость для получения текущего участника рабочего пространства
CurrentMemberDep = Annotated[Member, Depends(_get_current_member)]


def require_member_roles(
        *required_roles: MemberRole, allow_owner: bool = True
) -> Callable[[CurrentMemberDep], Member]:
    """Проверяет требование к ролям участника.

    :param required_roles: Запрашиваемые роли участника.
    :param allow_owner: Разрешить ли доступ к владельцу.
    """

    def dependency(member: CurrentMemberDep) -> Member:
        if allow_owner and member.is_owner:
            return member
        if required_roles and member.role not in required_roles:
            raise PermissionDeniedError(
                f"Required roles: {', '.join(required_roles)}. "
                f"Your role: `{member.role.value}`!",
                details={
                    "required_roles": required_roles,
                    "member_role": member.role.value,
                    "user_id": member.user_id,
                },
            )
        if not required_roles and not allow_owner:
            raise PermissionDeniedError("Access denied!")
        return member

    return dependency


# Требуется роль админа и выше
AdminOrHigherRequiredDep = Annotated[
    Member, Depends(require_member_roles(
        MemberRole.ADMIN, MemberRole.OWNER, allow_owner=True)
    )
]
# Требуется роль владельца
OwnerRequiredDep = Annotated[
    Member, Depends(require_member_roles(MemberRole.OWNER, allow_owner=True))
]
# Требуется роль менеджера или выше
ManagerOrHigherRequiredDep = Annotated[
    Member, Depends(require_member_roles(
        MemberRole.MANAGER, MemberRole.ADMIN, MemberRole.OWNER,
        allow_owner=True
    ))
]


def require_manager_or_higher_dep() -> Callable[[Member], Member]:
    return require_member_roles(
        MemberRole.MANAGER, MemberRole.ADMIN, MemberRole.OWNER,
        allow_owner=True
    )


# Требуется роль участника или выше
MemberOrHigherRequiredDep = Annotated[
    Member, Depends(require_member_roles(
        MemberRole.MEMBER, MemberRole.ADMIN, MemberRole.OWNER,
        allow_owner=False
    ))
]
