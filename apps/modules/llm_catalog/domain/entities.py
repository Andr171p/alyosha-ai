from typing import Self

from uuid import UUID

from pydantic import HttpUrl, ValidationError, model_validator

from modules.shared_kernel.domain import Entity

from .primitives import FeedbackRating
from .value_objects import (
    BillingTier,
    BusinessPresentation,
    Capabilities,
    CardStatus,
    HardwareRequirements,
    LLMCategory,
    PerformanceCharacteristics,
)


class UserFeedback(Entity):
    """Оценка пользователя на модель из каталога"""

    llm_card_id: UUID
    user_id: UUID
    rating: FeedbackRating
    review: str
    verified_usage: bool


class LLMCard(Entity):
    status: CardStatus
    category: LLMCategory
    name: str
    slug: str
    family: str
    description: str
    tags: set[str]
    provider_name: str
    source_url: HttpUrl
    capabilities: Capabilities
    performance_characteristics: PerformanceCharacteristics
    business_presentation: BusinessPresentation
    hardware_requirements: HardwareRequirements | None = None
    billing_tier: BillingTier | None = None

    @model_validator(mode="after")
    def validate_card_state(self) -> Self:
        """Проверка валидности карточки LLM"""

        if (
                self.category == LLMCategory.OPEN_SOURCE and
                self.billing_tier is not None and
                self.hardware_requirements is None
        ):
            raise ValidationError("Hardware requirements cannot be None for `open-source` LLM!")
        if self.category == LLMCategory.COMMERCIAL and self.billing_tier is None:
            raise ValidationError("Billing tier must be provided for `commercial` LLM!")
        return self
