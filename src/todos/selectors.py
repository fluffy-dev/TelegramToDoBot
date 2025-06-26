from django.contrib.auth.models import User
from django.db.models import QuerySet

from todos.models import Category, Task


def category_list_for_user(*, user: User) -> QuerySet[Category]:
    """
    Returns a queryset of categories for a given user.

    Args:
        user (User): The user for whom to retrieve categories.

    Returns:
        QuerySet[Category]: A queryset of categories.
    """
    return Category.objects.filter(user=user)


def task_list_for_user(*, user: User) -> QuerySet[Task]:
    """
    Returns a queryset of tasks for a given user.

    Args:
        user (User): The user for whom to retrieve tasks.

    Returns:
        QuerySet[Task]: A queryset of tasks.
    """
    return Task.objects.filter(user=user).prefetch_related('categories')