import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logger = logging.getLogger(__name__)

router = Router(name=__name__)


class MinutesForm(StatesGroup):
    """Форма для составления протокола совещания"""

    waiting_for_audio = State()
    indicates_speakers = State()
    in_output_format_select = State()


def get_output_format_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора формата документа с протоколом совещания"""

    builder = ReplyKeyboardBuilder()
    builder.button(text="docx")
    builder.button(text="pdf")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


@router.message(Command("minutes"))
async def cmd_minutes(message: Message, state: FSMContext) -> None:
    await message.answer("Отправьте аудио файл или голосовое сообщение")
    await state.set_state(MinutesForm.waiting_for_audio)


@router.message(MinutesForm.waiting_for_audio, F.voice | F.audio)
async def process_audio(message: Message, state: FSMContext) -> None:
    if message.audio:
        file_id = message.audio.file_id
        logger.info(
            "User `%s` upload audio file `%s`", message.from_user.username, message.audio.file_name
        )
    elif message.voice:
        file_id = message.voice.file_id
        logger.info(
            "User `%s` upload voice message with duration %s seconds",
            message.from_user.username, message.voice.duration
        )
    else:
        await message.answer("❌ Пожалуйста, отправьте аудио файл или голосовое сообщение")
        return
    await state.update_data(file_id=file_id)
    await message.answer(
        text="Выберите файл в котором вам удобнее получить протокол",
        reply_markup=get_output_format_kb()
    )
    await state.set_state(MinutesForm.in_output_format_select)


@router.message(MinutesForm.in_output_format_select, F.text)
async def process_output_format(message: Message, state: FSMContext) -> None:
    output_format = message.text
    if output_format not in {"docx", "pdf"}:
        ...
    logger.info(
        "User `%s` choose %s output format for minutes document",
        message.from_user.username, output_format
    )
    data = await state.get_data()
    await message.answer("Данные переданы ассистенту", reply_markup=ReplyKeyboardRemove())
    await create_minutes_task(
        user_id=message.from_user.id,
        file_ids=[data["file_id"]],
        document_ext=document_ext,
    )
