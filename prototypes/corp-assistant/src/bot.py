from enum import StrEnum

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .ai_agent import Context, call_agent
from .core.enums import UserRole
from .services import users
from .settings import settings

bot = Bot(token=settings.bot.token)

dp = Dispatcher(bot)


class Vote(StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class VoteCBData(CallbackData):
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


def get_admin_kb(user_id: int) -> InlineKeyboardMarkup: ...


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
        await message.reply("")
        return
    if existing_user.role in {UserRole.ADMIN, UserRole.MODERATOR}:
        await message.reply("", reply_markup=...)
    await message.reply("")


@dp.message()
async def handle_any_message(message: Message) -> None:
    tg_file_ids: set[str] = set()
    if message.audio is not None:
        tg_file_ids.add(message.audio.file_id)
    if message.voice is not None:
        tg_file_ids.add(message.voice.file_id)
    user = await users.get_by_user_id(message.from_user.id)
    ai_message = await call_agent(
        thread_id=f"{message.from_user.id}",
        human_text=message.text,
        context=Context(
            user_id=user.user_id, full_name=user.full_name, user_role=user.role
        ),
        tg_file_ids=list(tg_file_ids)
    )
    await message.reply(ai_message)


@dp.callback_query(VoteCBData)
async def handle_vote_callback(query: CallbackQuery, cb_data: VoteCBData) -> None:
    ...
