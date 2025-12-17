from typing import Any, Self, TypeVar, override

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from pydantic import EmailStr, Field, computed_field, model_validator

from config.dev import settings
from modules.shared_kernel.domain import Entity, InvariantViolationError
from modules.shared_kernel.utils import current_datetime

from ..utils.common import generate_guest_name
from .events import UserRegisteredEvent
from .exceptions import InvalidCredentialsError, UserNotEnabledError
from .value_objects import (
    AuthMethod,
    AuthProvider,
    ProfileInfo,
    UserCredentials,
    UserRole,
    UserStatus,
)


class SocialAccount(Entity):
    """Аккаунт пользователя у стороннего провайдера.

    Attributes:
        provider: Тип провайдера аутентификации.
        social_user_id: Идентификатор пользователя у внешнего провайдера.
        profile_info: Дополнительная информация об аккаунте.
    """

    provider: AuthProvider
    social_user_id: str
    profile_info: ProfileInfo

    @property
    def email(self) -> EmailStr | None:
        return self.profile_info.get("email")

    @classmethod
    def create(cls, provider: AuthProvider, social_user_id: str, **kwargs) -> Self:
        return cls(
            provider=provider,
            social_user_id=social_user_id,
            profile_info={"user_id": social_user_id, **kwargs},
        )


class BaseUser(Entity, ABC):
    """Базовая модель для имплементации пользователя"""

    username: str | None
    role: UserRole
    status: UserStatus

    @abstractmethod
    def to_jwt_payload(self, **kwargs) -> dict[str, Any]:
        """Полезная нагрузка для JWT"""


class User(BaseUser):
    """Модель пользователя.

    Примечания:
     - Не использовать model_dump или model_dump_json для маппинга полей,
       т.к секретные данные не будут сериализованы.

    Attributes:
        email: Адрес электронной почты пользователя
        username: Имя пользователя (как он будет отображаться в дисплеи)
        password_hash: Хэш пароля пользователя (имеется только при регистрации через credentials)
        role: Системная роль пользователя
        status: Системный статус пользователя
        social_accounts: Учётные записи внешних провайдеров
        auth_methods: Способы, которые может использовать пользователь для аутентификации
    """

    email: EmailStr | None = None
    password_hash: str | None = Field(default=None, exclude=True)
    social_accounts: list[SocialAccount] = Field(default_factory=list)
    auth_methods: set[AuthMethod] = Field(default_factory=set)

    @model_validator(mode="after")
    def _validate_invariant(self) -> Self:
        """Валидация инвариантов"""

        if self.status == UserStatus.PENDING_EMAIL_VERIFICATION and self.role != UserRole.GUEST:
            raise InvariantViolationError(
                "User role only can be `guest`, when status is `pending_email_verification`",
                entity_name=self.__class__.__name__,
                details={"user_id": f"{self.id}", "status": self.status, "role": self.role},
            )
        has_email, has_password_hash = self.email is not None, self.password_hash is not None
        if AuthMethod.CREDENTIALS in self.auth_methods:
            if not has_email:
                raise InvariantViolationError(
                    "Email is required for credentials authentication",
                    entity_name=self.__class__.__name__,
                    details={
                        "user_id": f"{self.id}",
                        "status": self.status,
                        "auth_methods": self.auth_methods
                    },
                )
            if not has_password_hash:
                raise InvariantViolationError(
                    "Password is required for credentials authentication",
                    entity_name=self.__class__.__name__,
                    details={"user_id": f"{self.id}", "status": self.status, "email": self.email},
                )
        return self

    def to_jwt_payload(self, **kwargs) -> dict[str, Any]:
        """Получение полезной нагрузки для JWT"""

        return {
            "iss": settings.app.url,
            "sub": f"{self.id}",
            "username": self.username,
            "email": f"{self.email}",
            "status": self.status.value,
            "role": self.role.value,
            **kwargs,
        }

    def is_registration_completed(self) -> bool:
        """Завершена ли регистрация успешно"""
        return self.status != UserStatus.PENDING_EMAIL_VERIFICATION

    def repeat_email_verification(self) -> None:
        """Повторение отправки письма для верификации email"""
        self._register_event(
            UserRegisteredEvent(user_id=self.id, user_status=self.status, email=self.email)
        )

    @classmethod
    def register_by_credentials(cls, credentials: UserCredentials) -> Self:

        from ..utils.security import hash_secret  # noqa: PLC0415

        user = cls(
            email=credentials.email,
            username=credentials.username,
            role=UserRole.GUEST,
            status=UserStatus.PENDING_EMAIL_VERIFICATION,
            password_hash=hash_secret(credentials.password),
            auth_methods={AuthMethod.CREDENTIALS}
        )
        cls._register_event(
            user, UserRegisteredEvent(user_id=user.id, user_status=user.status, email=user.email)
        )
        return user

    @classmethod
    def register_by_social_account(cls, social_account: SocialAccount) -> Self:
        status, role = (
            (UserStatus.PENDING_EMAIL_VERIFICATION, UserRole.GUEST)
            if social_account.email is None else
            (UserStatus.EMAIL_VERIFIED, UserRole.USER)
        )
        user = cls(
            email=social_account.email,
            status=status,
            role=role,
            social_accounts=[social_account],
            auth_mathods={AuthMethod.OAUTH2}
        )
        cls._register_event(
            user, UserRegisteredEvent(user_id=user.id, user_status=user.status, email=user.email)
        )
        return user

    def authenticate_by_credentials(self, credentials: UserCredentials) -> Self:

        from ..utils.security import verify_secret  # noqa: PLC0415

        if self.status in {UserStatus.BANNED, UserStatus.DELETED}:
            raise UserNotEnabledError(
                user_status=self.status,
                details={"user_id": self.id, "email": self.email, "username": self.username}
            )
        if not verify_secret(credentials.password, self.password_hash):
            raise InvalidCredentialsError(
                "Invalid password!",
                details={"user_id": self.id, "email": self.email, "username": self.username}
            )
        return self


class Guest(BaseUser):
    """Гость - пользователь, не прошедший регистрацию.
    Для предоставления временного доступа к контенту.
    """

    device_id: str | None = None
    expires_at: datetime = Field(..., frozen=True)
    username: str = Field(default_factory=generate_guest_name)
    role: UserRole = Field(default=UserRole.GUEST, frozen=True)
    status: UserStatus = Field(default=UserStatus.ANONYMOUS, frozen=True)

    @computed_field(description="Закончился ли гостевой период")
    def is_expired(self) -> bool:
        return current_datetime().timestamp() >= self.expires_at.timestamp()

    @override
    def to_jwt_payload(self, **kwargs) -> dict[str, Any]:
        """Получение полезной нагрузки для JWT"""

        return {
            "iss": settings.app.url,
            "sub": f"{self.id}",
            "device_id": self.device_id,
            "username": self.username,
            "status": self.status.value,
            "role": self.role.value,
            **kwargs,
        }

    @classmethod
    def create(cls, device_id: str | None = None) -> Self:
        """Фабричный метод для создания анонимного пользователя"""

        guest_expires_in = timedelta(days=settings.jwt.guest_access_token_expires_in_days)
        return cls(device_id=device_id, expires_at=current_datetime() + guest_expires_in)


AnyUser = TypeVar("AnyUser", bound=User | Guest)
