from typing import Any, Self

from abc import ABC, abstractmethod
from collections import UserList, UserString
from collections.abc import Callable

from pydantic_core import CoreSchema, core_schema


class StrPrimitive(str, ABC):  # noqa: SLOT000
    """Базовый класс для реализации строкового примитива.
    Для создания логики валидации нужно реализовать метод `validate`.
    """

    def __new__(cls, value: str) -> Self:
        value = cls.validate(value)
        return super().__new__(cls, value)

    @classmethod
    @abstractmethod
    def validate(cls, value: str) -> str:
        """Логика валидации и проверки значений строки"""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )


class CustomStrPrimitive(UserString):
    def __init__(self, seq: str) -> None:
        super().__init__(seq)
        self.data = self.validate(self.data)

    @classmethod
    def validate(cls, value: str) -> str:
        """Переопределить для реализации валидации"""

        return value

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )


class CustomListPrimitive(UserList):
    def __init__(self, initlist: list[Any]) -> None:
        super().__init__(initlist)
        self.data = self.validate(self.data)

    @classmethod
    def validate(cls, value: list[Any]) -> list[Any]:
        """Переопределить для реализации валидации"""

        return value

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )


class IntPrimitive(int, ABC):
    """Базовый класс для реализации цело-численного примитива.
    Для создания логики валидации нужно реализовать метод `validate`.
    """

    def __new__(cls, value: int, *args, **kwargs) -> Self:
        value = cls.validate(value, *args, **kwargs)
        return super().__new__(cls, value)

    @classmethod
    @abstractmethod
    def validate(cls, value: int, *args, **kwargs) -> int:
        """Логика валидации числа"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.int_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(int),
        )


class FloatPrimitive(float, ABC):
    """Базовый класс для реализации примитива с плавающей точкой.
    Для создания логики валидации нужно реализовать метод `validate`.
    """

    def __new__(cls, value: float, *args, **kwargs) -> Self:
        value = cls.validate(value, *args, **kwargs)
        return super().__new__(cls, value)

    @classmethod
    @abstractmethod
    def validate(cls, value: float, *args, **kwargs) -> int:
        """Логика валидации числа"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.float_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(float),
        )
