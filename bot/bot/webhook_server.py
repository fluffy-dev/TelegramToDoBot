import asyncio
import logging

from aiohttp import web
from aiogram import Bot

logger = logging.getLogger(__name__)


async def handle_notification(request: web.Request):
    """
    Handles incoming notification requests from the Django backend.
    """
    try:
        data = await request.json()
        telegram_id = data.get("telegram_id")
        message_text = data.get("message")
        bot: Bot = request.app["bot"]

        if not telegram_id or not message_text:
            logger.warning("Received invalid notification payload.")
            return web.json_response({"status": "bad_request"}, status=400)

        await bot.send_message(chat_id=telegram_id, text=message_text)
        logger.info(f"Sent notification to {telegram_id}")
        return web.json_response({"status": "ok"})

    except Exception as e:
        logger.error(f"Error handling notification: {e}")
        return web.json_response({"status": "error"}, status=500)


async def start_webhook_server(bot: Bot):
    """
    Starts the aiohttp web server for handling webhooks.
    """
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/notify", handle_notification)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    logger.info("Starting webhook server on port 8080...")
    await site.start()