import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs # <-- Импорт

from bot.config import BOT_TOKEN
from bot.handlers import common
from bot.dialogs.task_creation import create_task_dialog # <-- Импорт


async def main():
    """The main function to start the bot."""
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN environment variable is not set.")
        sys.exit(1)

    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=default_properties)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers and dialogs
    dp.include_router(common.router)
    dp.include_router(create_task_dialog)
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())