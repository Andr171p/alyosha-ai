from typing import NotRequired, TypedDict

from enum import StrEnum
from uuid import UUID

from pydantic import EmailStr, Field, HttpUrl, PositiveInt

from modules.shared_kernel.domain import ValueObject


class GuestSessionStatus(StrEnum):
    """Статус гостевой сессии

    Attributes:
        ACTIVE: Активная сессия, можно пользоваться гостевым функционалом.
        EXPIRED: Время сессии истекло.
        CONVERTED: Конвертирована в полноценного пользователя.
        LIMIT_EXCEEDED: Превышены лимиты.
    """

    ACTIVE = "active"
    EXPIRED = "expired"
    CONVERTED = "converted"
    LIMIT_EXCEEDED = "limit_exceeded"


class UserStatus(StrEnum):
    """Статус пользователя в системе

    Attributes:
        ANONYMOUS: Использует гостевой доступ.
        PENDING_EMAIL_VERIFICATION: Зарегистрирован через credentials, пока не подтвердил email.
        EMAIL_VERIFIED: Подтверждён email
        (автоматически устанавливается при регистрации через социальные сети)
        BANNED: Бан пользователя (ограничение действий)
        DELETED: Пользователь был удалён
    """

    ANONYMOUS = "anonymous"
    PENDING_EMAIL_VERIFICATION = "pending_email_verification"
    EMAIL_VERIFIED = "email_verified"
    BANNED = "banned"
    DELETED = "deleted"


class UserCredentials(ValueObject):
    """Учетные данные пользователя"""

    username: str
    email: EmailStr
    password: str


class UserRole(StrEnum):
    """Системные пользовательские роли.

    Attributes:
        SUPERADMIN: Полный доступ ко всей системе.
        ADMIN: Администратор с ограниченными правами
        MANAGER: Менеджер (управление пользователями/контентом).
        MODERATOR: # Модератор (модерация контента).
        USER: Обычный зарегистрированный пользователь.
        GUEST: Пользователь с неподтверждённым email.
    """

    SUPERADMIN = "superadmin"
    ADMIN = "workspaces"
    MANAGER = "manager"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class ProfileInfo(TypedDict):
    user_id: str
    email: NotRequired[EmailStr]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    avatar_url: NotRequired[HttpUrl]


class AuthMethod(StrEnum):
    """Возможные методы для регистрации и аутентификации пользователей"""

    CREDENTIALS = "credentials"
    OAUTH2 = "oauth2"


class AuthProvider(StrEnum):
    """Возможные внешние провайдеры для регистрации и аутентификации пользователей"""

    VK = "VK"
    Yandex = "Yandex"
    MAX = "Max"
    GOSUSLUGI = "Gosuslugi"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token(ValueObject):
    access_token: str
    token_type: str = Field(default="Bearer", frozen=True)
    expires_at: PositiveInt


class TokenPair(ValueObject):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="Bearer", frozen=True)
    expires_at: PositiveInt


class JWTClaims(ValueObject):
    """Базовая модель для интроспекции JWT"""

    active: bool = False
    cause: str | None = None
    token_type: TokenType | None = None
    iss: HttpUrl | None = None
    sub: str | None = None
    aud: str | None = None
    exp: int | float | None = None
    iat: int | float | None = None
    jti: UUID | None = None


class UserClaims(JWTClaims):
    username: str | None = None
    email: EmailStr | None = None
    status: UserStatus | None = None
    role: UserRole | None = None
