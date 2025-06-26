import logging

import redis.asyncio as redis
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, StartMode

from bot.dialogs.states import CreateTask, EditTask
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
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested tasks.")

    token = await get_user_token(user_id)
    if not token:
        logger.warning(f"No token found for user {user_id}. Asking to /start.")
        await message.answer("You are not authenticated. Please use /start first.")
        return

    api_client = ApiClient(base_url=API_BASE_URL, token=token)
    try:
        logger.info(f"Fetching tasks from API for user {user_id}.")
        tasks = await api_client.get_tasks()
        logger.info(f"Received {len(tasks)} tasks from API.")

        if not tasks:
            logger.info(f"No tasks for user {user_id}. Sending info message.")
            await message.answer("You have no tasks yet. Use /newtask to add one.")
            return

        logger.info(f"Looping through tasks to send messages for user {user_id}.")
        for task in tasks:
            task_id = task.get('id', 'NO_ID')
            logger.info(f"Processing task with id: {task_id} (len: {len(str(task_id))})")

            status = "✅" if task['is_completed'] else "❌"
            created_date = task['created_at'].split('T')[0]

            buttons = []
            if not task['is_completed']:
                complete_callback = f"task_complete:{task_id}"
                logger.info(f"  - Complete callback data: '{complete_callback}' (len: {len(complete_callback)})")
                buttons.append(
                    InlineKeyboardButton(text="Mark as Done ✅", callback_data=complete_callback)
                )

            edit_callback = f"task_edit:{task_id}"
            delete_callback = f"task_delete:{task_id}"
            logger.info(f"  - Edit callback data: '{edit_callback}' (len: {len(edit_callback)})")
            logger.info(f"  - Delete callback data: '{delete_callback}' (len: {len(delete_callback)})")

            buttons.extend([
                InlineKeyboardButton(text="Edit ✏️", callback_data=edit_callback),
                InlineKeyboardButton(text="Delete 🗑️", callback_data=delete_callback)
            ])

            keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

            response_text = (
                f"<b>{task['title']}</b> {status}\n"
                f"<i>Categories:</i> {', '.join([cat['name'] for cat in task.get('categories', [])]) or 'N/A'}\n"
                f"<i>Due:</i> {task.get('due_date', 'N/A')}\n"
                f"<i>Created:</i> {created_date}\n"
            )
            logger.info(f"Sending message for task {task_id}.")
            await message.answer(response_text, reply_markup=keyboard)
            logger.info(f"Message for task {task_id} sent.")

    except Exception as e:
        logger.error(f"Caught exception in cmd_tasks for user {user_id}: {e}", exc_info=True)
        await message.answer("Failed to fetch tasks. Please try again later.")

@router.message(F.text == "/newtask")
async def cmd_new_task(message: Message, dialog_manager: DialogManager):
    """Handler for starting the task creation dialog."""
    await dialog_manager.start(CreateTask.title, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith("task_complete:"))
async def handle_task_complete(callback: CallbackQuery):
    """Handles the 'Mark as Done' button press."""
    task_id = callback.data.split(":")[1]
    user_id = callback.from_user.id
    token = await get_user_token(user_id)

    if not token:
        await callback.answer("Authentication error. Please /start again.", show_alert=True)
        return

    api_client = ApiClient(base_url=API_BASE_URL, token=token)
    try:
        # Формируем payload только с теми данными, что меняем
        payload = {"is_completed": True}
        # Вызываем новый метод patch_task
        await api_client.patch_task(task_id, payload)

        # Обновляем текст сообщения, убираем кнопки
        await callback.message.edit_text(
            text=callback.message.text.replace("❌", "✅ Done!"),
            reply_markup=None
        )
        await callback.answer("Task marked as completed!")
    except Exception as e:
        logger.error(f"Failed to complete task {task_id} for user {user_id}: {e}")
        await callback.answer("Failed to update task.", show_alert=True)


@router.callback_query(F.data.startswith("task_edit:"))
async def handle_task_edit(callback: CallbackQuery, dialog_manager: DialogManager):
    """Handles the 'Edit' button press by starting the editing dialog."""
    task_id = callback.data.split(":")[1]
    await dialog_manager.start(
        EditTask.edit_categories,
        mode=StartMode.RESET_STACK,
        data={"task_id": task_id}
    )
    await callback.answer()  # Закрываем "часики" на кнопке


@router.callback_query(F.data.startswith("task_delete:"))
async def handle_task_delete(callback: CallbackQuery):
    """Handles the 'Delete' button press."""
    task_id = callback.data.split(":")[1]
    user_id = callback.from_user.id
    token = await get_user_token(user_id)

    if not token:
        await callback.answer("Authentication error. Please /start again.", show_alert=True)
        return

    api_client = ApiClient(base_url=API_BASE_URL, token=token)
    try:
        await api_client.delete_task(task_id)
        await callback.message.delete()  # Удаляем сообщение с задачей
        await callback.answer("Task deleted successfully!")
    except Exception as e:
        logger.error(f"Failed to delete task {task_id} for user {user_id}: {e}")
        await callback.answer("Failed to delete task.", show_alert=True)