from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token

from users.models import TelegramProfile


@transaction.atomic
def get_or_create_user_by_telegram_id(
    *,
    telegram_id: int,
    username: str
) -> tuple[User, Token]:
    """
    Retrieves or creates a user based on their Telegram ID.

    Args:
        telegram_id (int): The user's unique Telegram ID.
        username (str): The user's Telegram username.

    Returns:
        tuple[User, Token]: A tuple containing the user instance and their auth token.
    """
    try:
        profile = TelegramProfile.objects.select_related('user').get(telegram_id=telegram_id)
        user = profile.user
    except TelegramProfile.DoesNotExist:
        # Create a user with a unique username
        base_username = f"tg_{username or telegram_id}"
        unique_username = base_username
        counter = 1
        while User.objects.filter(username=unique_username).exists():
            unique_username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(username=unique_username)
        TelegramProfile.objects.create(user=user, telegram_id=telegram_id)

    token, _ = Token.objects.get_or_create(user=user)
    return user, token