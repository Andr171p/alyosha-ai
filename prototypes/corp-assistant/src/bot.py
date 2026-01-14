import logging
from enum import StrEnum

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .ai_agent import Context, call_agent
from .core.enums import UserRole
from .services import users
from .settings import settings
from .utils import current_datetime, escape_md2

logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))

dp = Dispatcher(storage=MemoryStorage())


class Vote(StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class VoteCBData(CallbackData, prefix="vote"):
    user_id: int
    message_id: int
    vote: Vote


def get_voting_kb(user_id: int, message_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👍", callback_data=VoteCBData(
        user_id=user_id, message_id=message_id, vote=Vote.LIKE
    ).pack())
    builder.button(text="👎", callback_data=VoteCBData(
        user_id=user_id, message_id=message_id, vote=Vote.DISLIKE
    ).pack())
    builder.adjust(1)
    return builder.as_markup()


def get_admin_menu_kb(user_id: int) -> InlineKeyboardMarkup: ...


@dp.message(CommandStart())
async def handle_start_cmd(message: Message) -> None:
    existing_user = await users.get_by_user_id(message.from_user.id)
    if existing_user is None:
        saved_user = await users.save(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        await message.reply(f"Привет **{saved_user.fist_name}**")
        return
    if existing_user.role in {UserRole.ADMIN, UserRole.MODERATOR}:
        await message.reply("...")
    await message.reply(f"С возвращением **{existing_user.fist_name}**")


@dp.message()
async def handle_any_message(message: Message) -> None:
    tg_file_id: str | None = None
    if message.audio is not None:
        tg_file_id = message.audio.file_id
    if message.voice is not None:
        tg_file_id = message.voice.file_id
    user = await users.get_by_user_id(message.from_user.id)
    ai_message = await call_agent(
        message_text=message.text or f"Создай протокол совещания для файла {tg_file_id}",
        context=Context(
            user_id=user.user_id, first_name=user.fist_name, user_role=user.role
        ),
        tg_user_message={
            "tg_message_id": message.message_id,
            "content_type": message.content_type,
            "tg_file_id": tg_file_id,
            "sent_at": current_datetime(),
        }
    )
    await message.reply(escape_md2(ai_message))
