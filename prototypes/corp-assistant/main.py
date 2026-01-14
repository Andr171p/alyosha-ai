import asyncio
import logging

from src.bot import bot, dp
from src.broker import app


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )


async def run_aiogram_bot() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def run_faststream_app() -> None:
    await app.broker.start()


async def main() -> None:
    await asyncio.gather(run_aiogram_bot(), run_faststream_app())


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
