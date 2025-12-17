from enum import StrEnum

from pydantic import HttpUrl

from modules.shared_kernel.domain import ValueObject

DEFAULT_TEMPERATURE = 0.7


class LLMProviderType(StrEnum):
    """Тип провайдера LLM"""

    OPENAI = "openai"
    GIGACHAT = "gigachat"
    YANDEX_CLOUD = "yandex-cloud"
    LOCAL = "local"


class ModelConfiguration(ValueObject):
    """Конфигурация модели"""

    provider_name: str
    provider_type: LLMProviderType
    apikey: str
    project: str
    model_name: str
    base_url: HttpUrl | None = None
    temperature: float = DEFAULT_TEMPERATURE
