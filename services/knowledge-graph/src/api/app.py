from fastapi import FastAPI

from .routers import router


def create_fastapi_app() -> FastAPI:
    app = FastAPI(title="Knowledge Graph API", version="0.0.1")
    app.include_router(router)
    return app
