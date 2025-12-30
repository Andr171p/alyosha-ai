from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    JsonField,
    JsonFieldNull,
    StrArray,
    StrText,
    UUIDField,
)


class LLMCardModel(Base):
    __tablename__ = "llm_cards"

    status: Mapped[str]
    category: Mapped[str]
    name: Mapped[str]
    slug: Mapped[str]
    family: Mapped[str]
    description: Mapped[StrText]
    tags: Mapped[StrArray]
    provider_name: Mapped[str]
    source_url: Mapped[str]
    capabilities: Mapped[JsonField]
    performance_characteristics: Mapped[JsonField]
    business_presentation: Mapped[JsonField]
    hardware_requirements: Mapped[JsonFieldNull]
    billing_tier: Mapped[JsonFieldNull]

    user_feedbacks: Mapped[list["UserFeedbackModel"]] = relationship(back_populates="llm_card")


class UserFeedbackModel(Base):
    __tablename__ = "user_feedbacks"

    llm_card_id: Mapped[UUID] = mapped_column(ForeignKey("llm_cards.id"), unique=False)
    user_id: Mapped[UUIDField]
    rating: Mapped[float]
    review: Mapped[StrText]
    verified_usage: Mapped[bool]

    llm_card: Mapped["LLMCardModel"] = relationship(back_populates="user_feedbacks")
