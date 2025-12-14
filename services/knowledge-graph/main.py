from typing import Final

import logging

import uvicorn
from fastapi import FastAPI

from src.api.app import create_fastapi_app

app: Final[FastAPI] = create_fastapi_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=8000,
        log_level="info",
        access_log=True,
    )
