from django.db import models
from django.conf import settings

from common.models import BaseModel


class Category(BaseModel):
    """
    Represents a category (or tag) for a task.

    Attributes:
        id (CharField): The primary key, a 64-character hash.
        name (CharField): The name of the category.
        user (ForeignKey): The user who owns this category.
    """
    id = models.CharField(
        primary_key=True,
        max_length=64,
        editable=False,
    )
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ('user', 'name')

    def __str__(self):
        """String representation of a Category."""
        return self.name


class Task(BaseModel):
    """
    Represents a single task in the ToDo list.

    Attributes:
        id (CharField): The primary key, a 64-character hash.
        title (CharField): The title of the task.
        description (TextField): A detailed description of the task.
        due_date (DateTimeField): The date and time when the task should be completed.
        is_completed (BooleanField): The completion status of the task.
        notification_sent (BooleanField): Flag to check if a notification was sent.
        user (ForeignKey): The user who owns this task.
        categories (ManyToManyField): The categories associated with this task.
    """
    id = models.CharField(
        primary_key=True,
        max_length=64,
        editable=False,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    categories = models.ManyToManyField(
        Category,
        related_name='tasks',
        blank=True
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        """String representation of a Task."""
        return self.title