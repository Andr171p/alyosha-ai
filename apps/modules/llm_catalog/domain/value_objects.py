from typing import ClassVar

from enum import StrEnum

from pydantic import (
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    computed_field,
)
from pydantic_extra_types.currency_code import Currency

from modules.shared_kernel.domain import ValueObject


class CardStatus(StrEnum):
    """Статус карточки.

    Attributes:
        PENDING: После заполнения карточки она (требует модерации и валидации).
        ACTIVE: Карточку можно отобразить пользователю.
        DEPRECATED: Карточка устарела (не показывать пользователю).
    """

    PENDING = "pending"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class LLMCategory(StrEnum):
    """Разделение LLM на 2 основные категории:
        - `open-source`: есть возможность локальной установки.
        - `commercial`: доступны по подписке через API.
     """

    OPEN_SOURCE = "open-source"
    COMMERCIAL = "commercial"


class BillingTier(ValueObject):
    """Рассчитан для модели тарификации - `pay-as-you-go`"""

    generation_cost_per_1k_tokens: NonNegativeFloat = Field(
        ..., description="Цена генерации 1000 токенов в валюте из поля `currency`"
    )
    currency: Currency = Field(..., description="Валюта в которой происходит расчёт")
    localized_price: NonNegativeFloat = Field(..., description="Цена относительно местного курса")


class HardwareRequirements(ValueObject):
    """Требования к 'железу'"""

    min_memory_gb: PositiveInt
    min_vram_gb: NonNegativeInt
    recommended_gpu: set[str] = Field(default_factory=set, examples=["RTX 4090", "A100"])
    cpu_requirements: str = Field(..., examples=["x86_64 with AVX2"])
    disk_space_gb: PositiveInt


class PerformanceCharacteristics(ValueObject):
    """Измеряемые метрики"""

    TOKENS_ON_PAGE: ClassVar[int] = 2000

    billion_params_count: PositiveInt = Field(..., description="Количество параметров LLM")
    context_window_tokens: PositiveInt = Field(..., description="Длина контекста в токенах")

    @computed_field(description="User-friendly формат (контекстное окно - количество страниц")
    def context_window_pages(self) -> PositiveInt:
        return self.context_window_tokens / self.TOKENS_ON_PAGE


class Modality(StrEnum):
    """Виды модальностей"""

    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class Capabilities(ValueObject):
    """Возможности LLM"""

    languages: set[str] = Field(
        default_factory=set,
        description="Основные языки, которые поддерживает LLM",
        examples=["ru", "en"]
    )
    modalities: set[Modality] = Field(
        default_factory=set, description="Модальности (типы данных) с которыми работает LLM"
    )
    features: set[str] = Field(
        default_factory=set,
        description="Технические возможности LLM",
        examples=["FUNCTION_CALLING", "JSON_MODE", "STREAMING", "REASONING"]
    )


class ExamplePrompt(ValueObject):
    """Простой пример промпта для LLM"""

    task: str
    example_input: str
    example_output: str


class BusinessPresentation(ValueObject):
    """Удобная бизнес интерпретация LLM"""

    use_case_tags: set[str] = Field(
        default_factory=set, examples=["АНАЛИЗ_ДОКУМЕНТОВ", "ЧАТ_ПОДДЕРЖКА"]
    )
    industry_tags: set[str] = Field(
        default_factory=set, examples=["ФИНТЕХ", "РИТЕЙЛ", "ГОС_СЕКТОР"]
    )
    tagline: str = Field(
        ..., description="Слоган модели", examples=["Лучшая модель для анализа на русском"]
    )
