from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...application import verify_token
from ...application.dto import CurrentUser
from ...application.exceptions import UnauthorizedError
from ...domain import TokenType


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


CurrentUserDep = Annotated[CurrentUser, Depends(_get_current_user)]
