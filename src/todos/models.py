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