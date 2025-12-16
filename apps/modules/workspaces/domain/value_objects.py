from enum import StrEnum


class InvitationStatus(StrEnum):
    """Статус приглашения"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"


class WorkspaceType(StrEnum):
    """Тип рабочего пространства"""

    PUBLIC = "public"
    PRIVATE = "private"


class OrganizationType(StrEnum):
    """Тип организации"""

    # Коммерческие организации
    CORPORATION = "corporation"
    SMALL_BUSINESS = "small_business"
    STARTUP = "startup"
    # Образовательные учреждения
    UNIVERSITY = "university"
    SCHOOL = "school"
    # Государственные структуры
    GOVERNMENT = "government"
    # Сфера услуг
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    CONSULTING = "consulting"
    RETAIL = "retail"
    # Креативные индустрии
    MEDIA = "media"
    ADVERTISING = "advertising"
    DESIGN = "design"
    # Другое
    OTHER = "other"


class MemberRole(StrEnum):
    """Роли внутри рабочего пространства.

    Attributes:
        OWNER: Полный контроль над workspace. Не может быть удален.
        ADMIN: Управление workspace, кроме финансовых операций.
        MANAGER: Руководитель (с правами на свою команду).
        MEMBER: Основной рабочий пользователь.
        GUEST: Ограниченный доступ для внешних лиц.
    """

    OWNER = "owner"
    ADMIN = "workspaces"
    MANAGER = "manager"
    MEMBER = "member"
    GUEST = "guest"


class MemberStatus(StrEnum):
    """Статус участника"""

    PENDING = "pending"
    ACTIVE = "active"
    BANNED = "banned"
    DELETED = "deleted"
