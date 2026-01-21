import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .bot import bot, dp
from .broker import app as faststream_app

logger = logging.getLogger(__name__)

WEBHOOK_URL = "http://localhost:8000/hook"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await faststream_app.broker.start()
    await bot.set_webhook(
        url=WEBHOOK_URL, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True
    )
    logger.info("Telegram Bot webhook set to %s", WEBHOOK_URL)
    yield
    await bot.delete_webhook()
    logger.info("Telegram Bot webhook removed")
    await faststream_app.broker.stop()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/hook")
async def handle_aiogram_bot_update(request: Request) -> None:
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot=bot, update=update)


@app.post("api/v1/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...)) -> None: ...
