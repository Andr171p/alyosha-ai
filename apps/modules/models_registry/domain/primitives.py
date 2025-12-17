from modules.shared_kernel.domain import IntPrimitive, StrPrimitive


class ModelSlug(StrPrimitive):
    """Идентификатор модели, например `deepseek-ai/DeepSeek-V3`"""

    @classmethod
    def validate(cls, slug: str) -> str: ...


class ModelRating(IntPrimitive):
    """Рейтинг модели от 1 до 5"""

    MIN_RATING, MAX_RATING = 1, 5

    @classmethod
    def validate(cls, rating: int, *args, **kwargs) -> int:  # noqa: ARG003
        if not (cls.MIN_RATING <= rating <= cls.MAX_RATING):
            raise ValueError("Model rating must be in between 1 and 5")
        return rating
