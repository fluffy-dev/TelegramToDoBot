import operator
from datetime import datetime

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Multiselect, Next, Start, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format

from bot.api_client import ApiClient
from bot.config import API_BASE_URL
from bot.dialogs.states import CreateTask
from bot.handlers.common import get_user_token


# --- Handlers ---

async def on_title_entered(message: Message, widget: MessageInput, manager: DialogManager):
    manager.dialog_data['title'] = message.text
    await manager.next()


async def on_description_entered(message: Message, widget: MessageInput, manager: DialogManager):
    manager.dialog_data['description'] = message.text
    await manager.next()


async def on_due_date_entered(message: Message, widget: MessageInput, manager: DialogManager):
    try:
        # Простая валидация формата. В реальном проекте лучше использовать календарь.
        datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        manager.dialog_data['due_date'] = message.text
        await on_task_create(message, manager)
    except ValueError:
        await message.answer("Invalid date format. Please use YYYY-MM-DD HH:MM.")


async def on_task_create(message: Message, manager: DialogManager):
    user_id = message.from_user.id
    token = await get_user_token(user_id)
    if not token:
        await message.answer("Authentication error. Please /start again.")
        await manager.done()
        return

    api_client = ApiClient(API_BASE_URL, token)
    dialog_data = manager.dialog_data
    selected_categories = manager.find("category_multiselect").get_checked()

    try:
        await api_client.create_task(
            title=dialog_data.get("title"),
            description=dialog_data.get("description"),
            due_date=dialog_data.get("due_date"),
            category_ids=selected_categories
        )
        await message.answer("✅ Task created successfully!")
    except Exception as e:
        await message.answer(f"Failed to create task: {e}")
    finally:
        await manager.done()


# --- Getters for dynamic data ---

async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    token = await get_user_token(user_id)
    if not token:
        return {"categories": []}

    api_client = ApiClient(API_BASE_URL, token)
    try:
        categories = await api_client.get_categories()
        # aiogram-dialog требует кортеж из (название, id)
        return {"categories": [(cat["name"], cat["id"]) for cat in categories]}
    except Exception:
        return {"categories": []}


# --- Dialog definition ---

create_task_dialog = Dialog(
    Window(
        Const("Let's create a new task.\n\nPlease enter the title:"),
        MessageInput(on_title_entered),
        state=CreateTask.title,
    ),
    Window(
        Const("Great! Now enter the description:"),
        MessageInput(on_description_entered),
        Back(),
        state=CreateTask.description,
    ),
    Window(
        Const("Choose categories (optional):"),
        Multiselect(
            Format("✓ {item[0]}"),  # text for selected item
            Format("{item[0]}"),   # text for unselected item
            id="category_multiselect",
            item_id_getter=operator.itemgetter(1),
            items="categories",
        ),
        getter=get_categories_data,
        state=CreateTask.categories,
        # Кнопка "Далее" для пропуска, если не выбрано ни одной категории
        Next(Const("Next >>")),
        Back(Const("<< Back")),
    ),
    Window(
        Const("Finally, enter the due date in YYYY-MM-DD HH:MM format:"),
        MessageInput(on_due_date_entered),
        Back(),
        state=CreateTask.due_date,
    ),
)