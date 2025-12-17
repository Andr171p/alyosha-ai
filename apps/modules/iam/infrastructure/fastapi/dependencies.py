from typing import Annotated

from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...application import verify_token
from ...application.dto import CurrentUser
from ...application.exceptions import UnauthorizedError
from ...domain import TokenType, UserRole
from ...domain.exceptions import PermissionDeniedError


def _get_current_user(
        request: Request,    # noqa: ARG001
        credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False))
) -> CurrentUser:
    """Зависимость для получения текущего пользователя"""

    if not credentials:
        raise UnauthorizedError("Authentication required, missing credentials!")
    token = credentials.credentials
    claims = verify_token(token)
    if not claims.active:
        raise UnauthorizedError(
            f"Token is not active by cause: {claims.cause}, please login again"
        )
    if claims.token_type != TokenType.ACCESS:
        raise UnauthorizedError("Invalid token type!")
    return CurrentUser.model_validate({
            "user_id": claims.sub,
            "username": claims.username,
            "email": claims.email,
            "status": claims.status,
            "role": claims.role,
        })


# Зависимость для получения текущего пользователя
CurrentUserDep = Annotated[CurrentUser, Depends(_get_current_user)]


def require_user_roles(*required_roles: UserRole) -> Callable[[CurrentUserDep], CurrentUser]:
    """Проверка требуемых ролей у пользователя.

    :param required_roles: Запрашиваемые роли.
    """

    def dependency(current_user: CurrentUserDep) -> CurrentUser:
        if required_roles and current_user.role not in required_roles:
            raise PermissionDeniedError(
                f"Required roles: {', '.join(required_roles)}. "
                f"Your role: `{current_user.role.value}`!",
                details={
                    "required_roles": required_roles,
                    "user_role": current_user.role.value,
                    "user_id": current_user.user_id,
                },
            )
        if not required_roles:
            raise PermissionDeniedError("Access denied!")
        return current_user

    return dependency
