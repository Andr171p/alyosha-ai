from pydantic import Field, PositiveInt

from modules.shared_kernel.application import DTO

from ..domain import LLMCategory, ModalityType, ModelCapability, SizeType


class LLMFilters(DTO):
    categories: set[LLMCategory] = Field(default_factory=set, description="По категории")
    size_types: set[SizeType] = Field(default_factory=set, description="По размеру")
    min_params: PositiveInt | None = Field(
        default=7, description="Минимальное количество параметров"
    )
    max_params: PositiveInt | None = Field(
        default=None, description="Максимальное количество параметров"
    )
    capabilities: set[ModelCapability] = Field(default_factory=set, description="Возможности LLM")
    modalities: set[ModalityType] = Field(default_factory=set, description="Виды модальности")
    provider_names: set[str] = Field(default_factory=set, description="По именам провайдеров")
