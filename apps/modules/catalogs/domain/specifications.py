from typing import TypeVar

from abc import ABC, abstractmethod

T = TypeVar("T")


class Specification[T: ...](ABC):

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Проверка на удовлетворение кандидата заданному условию"""

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        """Логическое `И`"""
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        """Логическое ИЛИ"""
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        """Логическое НЕ"""
        return NotSpecification(self)


class CompositeSpecification(Specification[T], ABC):
    """Базовый класс для составных спецификаций"""

    def __init__(self, *specifications: Specification[T]) -> None:
        self.specifications = specifications


class AndSpecification(CompositeSpecification[T]):
    """Спецификация `И`"""

    def is_satisfied_by(self, candidate: T) -> bool:
        return all(
            specification.is_satisfied_by(candidate) for specification in self.specifications
        )


class OrSpecification(CompositeSpecification[T]):
    """Спецификация `ИЛИ`"""

    def is_satisfied_by(self, candidate: T) -> bool:
        return any(
            specification.is_satisfied_by(candidate) for specification in self.specifications
        )


class NotSpecification(Specification[T]):
    """Спецификация `НЕ`"""

    def __init__(self, specification: Specification[T]) -> None:
        self.specification = specification

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.specification.is_satisfied_by(candidate)


class TagSpecification(Specification[T]):
    """Спецификация для фильтрации по тегам"""

    def __init__(self, tags: list[str], match_all: bool = False) -> None:
        self.tags = set(tags)
        self.match_all = match_all

    def is_satisfied_by(self, candidate: T) -> bool:
        if not hasattr(candidate, "tags"):
            return False
        candidate_tags = set(candidate.tags)
        if self.match_all:
            return self.tags.issubset(candidate_tags)
        return bool(self.tags & candidate_tags)
