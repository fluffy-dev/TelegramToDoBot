from aiogram.fsm.state import State, StatesGroup


class CreateTask(StatesGroup):
    """
    States for the task creation dialog.
    """
    title = State()
    description = State()
    categories = State()
    due_date = State()

class EditTask(StatesGroup):
    """States for the task editing dialog."""
    choose_action = State()
    edit_categories = State()