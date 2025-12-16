from typing import Any

from uuid import UUID

from ..domain import AppError, ErrorType


class NotFoundError(AppError):
    def __init__(
            self, message: str, entity_name: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            type=ErrorType.NOT_FOUND,
            code=f"{entity_name.upper()}_NOT_FOUND",
            details=details
        )


class ConflictError(AppError):
    """Конфликт связанный с целостностью данных"""

    def __init__(
            self,
            entity_name: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Data conflict for {entity_name}",
            type=ErrorType.CONFLICT,
            code=f"{entity_name.upper()}_CONFLICT",
            details=details,
            original_error=original_error
        )


class CreationError(AppError):
    """Ошибка при создании записи в ресурса"""

    def __init__(
            self,
            entity_name: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while {entity_name} creation",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="CREATION_FAILED",
            details=details,
            original_error=original_error
        )


class ReadingError(AppError):
    """Ошибка при чтении данных"""

    def __init__(
            self,
            entity_name: str,
            entity_id: UUID | str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while reading {entity_name} by {entity_id}",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="READING_FAILED",
            details=details,
            original_error=original_error
        )


class UpdateError(AppError):
    """Ошибка при обновлении ресурса"""

    def __init__(
            self,
            entity_name: str,
            entity_id: UUID | str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while update {entity_name} by {entity_id}",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="UPDATE_FAILED",
            details=details,
            original_error=original_error
        )


class DeleteError(AppError):
    """Ошибка при удалении ресурса"""

    def __init__(
            self,
            entity_name: str,
            entity_id: UUID | str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while delete {entity_name} by {entity_id}",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="DELETE_FAILED",
            details=details,
            original_error=original_error
        )


class CacheHitError(AppError):
    """Ошибка при получении данных из кеша"""

    def __init__(
            self,
            key: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while cache receiving by key {key}",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="CACHE_HIT_FAILED",
            original_error=original_error,
            details=details
        )


class CacheSetError(AppError):
    """Ошибка при добавлении данных в кеш"""

    def __init__(
        self,
        key: str,
        value: dict[str, Any],
        details: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Error occurred while cache set by key {key}, value {value}",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="CACHE_SET_FAILED",
            original_error=original_error,
            details=details,
        )


class CacheInvalidationError(AppError):
    """Ошибка при инвалидации данных из кеша"""

    def __init__(
        self,
        key: str,
        details: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Error occurred while cache invalidation by key {key}",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="CACHE_INVALIDATION_FAILED",
            original_error=original_error,
            details=details,
        )
