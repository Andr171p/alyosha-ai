from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class AuthenticationError(AppError):
    """Ошибка в момент аутентификации"""

    def __init__(self, message: str, details: dict[str, Any]) -> None:
        super().__init__(
            message=message,
            type=ErrorType.UNAUTHORIZED,
            code="AUTHENTICATION_FAILED",
            details=details,
        )


class InvalidCredentialsError(AppError):
    """Неверные учётные данные пользователя"""

    def __init__(self, message: str, details: dict[str, Any]) -> None:
        super().__init__(
            message=message,
            type=ErrorType.UNAUTHORIZED,
            code="INVALID_CREDENTIALS",
            details=details,
        )


class UserNotEnabledError(AppError):
    """Пользователь не доступен для аутентификации"""

    def __init__(self, user_status: str, details: dict[str, Any]) -> None:
        super().__init__(
            message=f"User not enabled with status {user_status}",
            type=ErrorType.PERMISSION_DENIED,
            code="PERMISSION_DENIED",
            details=details,
        )


class TokenExpiredError(AppError):
    """Токен больше не действителен (протух)"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message, code="TOKEN_EXPIRED", type=ErrorType.UNAUTHORIZED, details=details
        )


class InvalidTokenError(AppError):
    """Неверный токен"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message, code="INVALID_TOKEN", type=ErrorType.UNAUTHORIZED, details=details
        )


class PermissionDeniedError(AppError):
    """Недостаточно прав"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            type=ErrorType.PERMISSION_DENIED,
            details=details
        )


class DecryptionError(AppError):
    """Ошибка дешифрования"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.VALIDATION_ERROR,
            code="DECRYPTION_FAILED",
            details=details
        )
