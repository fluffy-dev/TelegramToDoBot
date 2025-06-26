from django.db import models
from django.conf import settings


class TelegramProfile(models.Model):
    """
    Links a Django User to a Telegram user ID.

    Attributes:
        user (OneToOneField): The Django user instance.
        telegram_id (BigIntegerField): The unique identifier from Telegram.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_profile'
    )
    telegram_id = models.BigIntegerField(unique=True)

    def __str__(self):
        """String representation of a TelegramProfile."""
        return f"{self.user.username} - {self.telegram_id}"