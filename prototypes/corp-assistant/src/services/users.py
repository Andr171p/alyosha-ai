from sqlalchemy import select

from ..core import enums, schemas
from ..database import crud, models
from ..database.base import sessionmaker


async def get_by_user_id(user_id: int) -> schemas.User | None:
    async with sessionmaker() as session:
        stmt = select(models.User).where(models.User.user_id == user_id)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
    if model is None:
        return None
    return schemas.User.model_validate(model)


async def save(
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        role: enums.UserRole = enums.UserRole.USER
) -> schemas.User:
    user = schemas.User(
        user_id=user_id,
        username=username,
        fist_name=first_name,
        last_name=last_name,
        role=role
    )
    await crud.create(user, model_class=models.User)
    return user
