import httpx
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from todos.models import Task


logger = get_task_logger(__name__)


@shared_task
def send_due_task_notification(task_id: str):
    """
    Handles the logic for a single due task:
    1. Marks it as notified.
    2. Sends a notification to the user via the bot's webhook.
    """
    from todos.services import task_set_notification_sent

    try:
        task = Task.objects.select_related('user__telegram_profile').get(id=task_id)
        task_set_notification_sent(task=task)
        logger.info(f"Notification flag set for task {task_id}")

        # Вызываем webhook бота
        telegram_id = task.user.telegram_profile.telegram_id
        message_text = f"🔔 Reminder! Your task '{task.title}' is due now."
        webhook_url = settings.BOT_WEBHOOK_URL

        payload = {"telegram_id": telegram_id, "message": message_text}

        with httpx.Client() as client:
            response = client.post(webhook_url, json=payload)
            response.raise_for_status()

        logger.info(f"Successfully triggered webhook for task {task_id}")

    except Task.DoesNotExist:
        logger.warning(f"Task with id {task_id} not found.")
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")


@shared_task
def check_for_due_tasks():
    """
    Periodically checks for due tasks and triggers individual notification tasks.
    """
    from todos.selectors import get_due_tasks_for_notification

    logger.info("Checking for due tasks...")
    due_tasks = get_due_tasks_for_notification()

    if not due_tasks:
        logger.info("No due tasks found.")
        return

    for task in due_tasks:
        logger.info(f"Found due task: {task.id}. Triggering notification.")
        send_due_task_notification.delay(task.id)

    logger.info(f"Triggered notifications for {due_tasks.count()} tasks.")