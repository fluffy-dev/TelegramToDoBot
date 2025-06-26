import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties # <-- Импортируем новый класс
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.handlers import common


async def main():
    """The main function to start the bot."""
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN environment variable is not set.")
        sys.exit(1)

    # Создаем объект с настройками по умолчанию
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

    # Передаем его в конструктор Bot через аргумент `default`
    bot = Bot(token=BOT_TOKEN, default=default_properties)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(common.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())