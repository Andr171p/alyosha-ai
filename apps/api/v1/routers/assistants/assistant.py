from fastapi import APIRouter, status

router = APIRouter(prefix="/assistants", tags=["Assistants"])


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Создать AI ассистента"
)
async def create_assistant() -> ...: ...
