from typing import Literal

from enum import StrEnum

from pydantic import PositiveInt

from modules.shared_kernel.domain import ValueObject


class DeploymentType(StrEnum):
    """Тип развёртывания модели"""

    LOCAL = "local"
    CLOUD = "cloud"


class ModelCapability(StrEnum):
    """Возможности модели"""

    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    VISION = "vision"
    TRANSLATION = "translation"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"
    MATH = "math"


class ModelTask(StrEnum):
    """Задачи выполняемые моделью"""

    IMAGE2TEXT = "image-to-text"
    STT = "speech-to-text"
    TTS = "text-to-speech"
    QA = "question-answering"
    ANY2ANY = "any2any"


class ModelModality(StrEnum):
    """Модальность модели (с какими данными работает модель)"""

    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class ArchitectureType(StrEnum):
    """Тип архитектуры модели"""

    # Основные архитектуры трансформеров
    TRANSFORMER = "transformer"
    GPT = "gpt"
    BERT = "bert"
    T5 = "t5"
    # Специализированные
    MULTI_MODAL_TRANSFORMER = "multimodal-transformer"
    CODE_SPECIFIC = "code-specific"


class ModelSpecification(ValueObject):
    """Технические характеристики модели

    Attributes:
        params_count: Количество параметров.
        architecture: Тип архитектуры.
        max_sequence_length: Максимальная длина контекста.
    """

    unit_of_params: Literal["M", "B"]
    params_count: PositiveInt
    architecture: ArchitectureType
    max_sequence_length: PositiveInt
