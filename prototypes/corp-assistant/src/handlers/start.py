from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from ..keyboards import get_admin_menu_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    if users.is_admin(user_id):
        admin = await users.get(user_id)
        if admin is None:
            await users.save(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                role=UserRole.ADMIN,
            )
        await message.reply("Админ панель", reply_markup=get_admin_menu_kb(user_id))
        return
    user = await users.get(user_id)
    if user is None:
        await users.save(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    await message.reply(f"Добро пожаловать <b>{user.fist_name}</b>")
