__all__ = ("router",)

from fastapi import APIRouter

from .documents import router as documents_router

router = APIRouter(prefix="/api/v1")

router.include_router(documents_router)
