import datetime
import hashlib

from typing import Optional

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from common.services import model_update
from todos.models import Category, Task


def _generate_hash_id(*, user_id: int, identifier: str) -> str:
    """
    Generates a SHA-1 hash to be used as a primary key.

    Args:
        user_id (int): The ID of the user creating the object.
        identifier (str): A unique string for the object (e.g., title).

    Returns:
        str: A 40-character hexadecimal string.
    """
    now_iso = timezone.now().isoformat()
    creation_string = f"{user_id}:{identifier}:{now_iso}"
    # Меняем sha256 на sha1
    return hashlib.sha1(creation_string.encode('utf-8')).hexdigest()


@transaction.atomic
def category_create(
    *,
    user: User,
    name: str
) -> Category:
    """
    Creates a new category.

    Args:
        user (User): The user creating the category.
        name (str): The name of the category.

    Returns:
        Category: The newly created category instance.
    """
    category_id = _generate_hash_id(user_id=user.id, identifier=name)
    category = Category(id=category_id, user=user, name=name)
    category.full_clean()
    category.save()

    return category


@transaction.atomic
def task_create(
    *,
    user: User,
    title: str,
    due_date: datetime.datetime,
    description: Optional[str] = "",
    categories: Optional[list[Category]] = None,
) -> Task:
    """
    Creates a new task.

    Args:
        user (User): The user creating the task.
        title (str): The title of the task.
        due_date (datetime): The due date for the task.
        description (str, optional): The description of the task.
        categories (list[Category], optional): A list of categories for the task.

    Returns:
        Task: The newly created task instance.
    """
    task_id = _generate_hash_id(user_id=user.id, identifier=title)
    task = Task(
        id=task_id,
        user=user,
        title=title,
        description=description,
        due_date=due_date
    )
    task.full_clean()
    task.save()

    if categories:
        task.categories.set(categories)

    return task


@transaction.atomic
def task_update(*, task: Task, data: dict) -> Task:
    """
    Updates an existing task.

    Args:
        task (Task): The task instance to update.
        data (dict): A dictionary containing the new data.

    Returns:
        Task: The updated task instance.
    """
    non_side_effect_fields = [
        'title', 'description', 'due_date', 'is_completed'
    ]
    task, has_updated = model_update(
        instance=task,
        fields=non_side_effect_fields,
        data=data
    )

    if 'categories' in data:
        task.categories.set(data['categories'])

    return task

@transaction.atomic
def task_set_notification_sent(*, task: Task) -> Task:
    """
    Marks a task's notification as sent to prevent re-sending.

    Args:
        task (Task): The task instance to update.

    Returns:
        Task: The updated task instance.
    """
    if task.notification_sent:
        raise ValidationError("Notification has already been sent for this task.")

    task.notification_sent = True
    task.full_clean(exclude=['user', 'categories'])
    task.save(update_fields=['notification_sent'])

    return task