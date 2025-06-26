import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Multiselect, Cancel
from aiogram_dialog.widgets.text import Const, Format

from bot.api_client import ApiClient
from bot.config import API_BASE_URL
from bot.dialogs.states import EditTask
from bot.handlers.common import get_user_token


async def get_task_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    token = await get_user_token(user_id)
    task_id = dialog_manager.start_data.get("task_id")
    if not token or not task_id: return {}

    api_client = ApiClient(API_BASE_URL, token)
    try:
        task = await api_client.get_task(task_id)
        all_categories = await api_client.get_categories()

        current_category_ids = [cat['id'] for cat in task.get('categories', [])]
        dialog_manager.dialog_data["category_multiselect_edit"] = current_category_ids

        return {
            "task_title": task.get("title"),
            "categories": [(cat["name"], cat["id"]) for cat in all_categories]
        }
    except Exception:
        return {}


async def on_save_categories(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = manager.event.from_user.id
    token = await get_user_token(user_id)
    task_id = manager.start_data.get("task_id")
    if not token or not task_id:
        await callback.answer("Error: session expired.", show_alert=True)
        await manager.done()
        return

    api_client = ApiClient(API_BASE_URL, token)
    selected_ids = manager.find("category_multiselect_edit").get_checked()

    try:
        current_task = await api_client.get_task(task_id)
        payload = {
            "title": current_task['title'],
            "description": current_task['description'],
            "due_date": current_task['due_date'],
            "is_completed": current_task['is_completed'],
            "categories": selected_ids
        }
        await api_client.update_task(task_id, payload)
        await callback.answer("Categories updated!", show_alert=True)
    except Exception as e:
        await callback.answer(f"Failed to update categories: {e}", show_alert=True)

    await manager.done()


edit_task_dialog = Dialog(
    Window(
        Format("Editing task: <b>{task_title}</b>"),
        Const("Select new categories:"),
        Multiselect(
            Format("✓ {item[0]}"),
            Format("{item[0]}"),
            id="category_multiselect_edit",
            item_id_getter=operator.itemgetter(1),
            items="categories",
        ),
        Button(Const("Save Changes"), id="save_cats", on_click=on_save_categories),
        Cancel(Const("Close")),
        getter=get_task_data,
        state=EditTask.edit_categories,
    )
)