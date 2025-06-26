import logging

import redis.asyncio as redis
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.dialogs.states import CreateTask
from bot.api_client import ApiClient
from bot.config import API_BASE_URL, REDIS_URL



router = Router()
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
logger = logging.getLogger(__name__)

TOKEN_KEY_PREFIX = "user_token:"


async def get_user_token(user_id: int) -> str | None:
    """
    Retrieves a user's API token from Redis.

    Args:
        user_id: The Telegram user ID.

    Returns:
        The token string if found, otherwise None.
    """
    return await redis_client.get(f"{TOKEN_KEY_PREFIX}{user_id}")


async def set_user_token(user_id: int, token: str):
    """
    Saves a user's API token to Redis.

    Args:
        user_id: The Telegram user ID.
        token: The API token string to save.
    """
    await redis_client.set(f"{TOKEN_KEY_PREFIX}{user_id}", token)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handler for the /start command."""
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)

    api_client = ApiClient(base_url=API_BASE_URL)
    try:
        token = await api_client.authenticate(telegram_id=user_id, username=username)
        await set_user_token(user_id, token)
        logger.info(f"Successfully authenticated user {user_id}")
        await message.answer(
            "Welcome to the ToDo List Bot!\n"
            "You are successfully authenticated.\n\n"
            "Available commands:\n"
            "/tasks - View your tasks\n"
            "/newtask - Add a new task"
        )
    except Exception as e:
        logger.error(f"Authentication failed for user {user_id}: {e}")
        await message.answer(f"Authentication failed. Please try again later.")


@router.message(F.text == "/tasks")
async def cmd_tasks(message: Message):
    """Handler for the /tasks command."""
    user_id = message.from_user.id
    token = await get_user_token(user_id)

    if not token:
        await message.answer("You are not authenticated. Please use /start first.")
        return

    api_client = ApiClient(base_url=API_BASE_URL, token=token)
    try:
        tasks = await api_client.get_tasks()
        if not tasks:
            await message.answer("You have no tasks yet. Use /newtask to add one.")
            return

        response_text = "<b>Your tasks:</b>\n\n"
        for task in tasks:
            categories = ", ".join([cat['name'] for cat in task['categories']])
            status = "✅" if task['is_completed'] else "❌"
            # Форматируем дату для лучшей читаемости
            created_date = task['created_at'].split('T')[0]

            response_text += (
                f"<b>{task['title']}</b> {status}\n"
                f"<i>Categories:</i> {categories or 'N/A'}\n"
                f"<i>Due:</i> {task['due_date']}\n"
                f"<i>Created:</i> {created_date}\n"
                "--------------------\n"
            )
        await message.answer(response_text)
    except Exception as e:
        logger.error(f"Failed to fetch tasks for user {user_id}: {e}")
        await message.answer("Failed to fetch tasks. Please try again later.")

@router.message(F.text == "/newtask")
async def cmd_new_task(message: Message, dialog_manager: DialogManager):
    """Handler for starting the task creation dialog."""
    await dialog_manager.start(CreateTask.title, mode=StartMode.RESET_STACK)