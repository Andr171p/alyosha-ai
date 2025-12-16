from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class PermissionDeniedError(AppError):
    """Недостаточно прав"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.PERMISSION_DENIED,
            code="PERMISSION_DENIED",
            details=details
        )
