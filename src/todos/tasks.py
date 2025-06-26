from celery import shared_task
from celery.utils.log import get_task_logger

from todos.models import Task


logger = get_task_logger(__name__)


@shared_task
def send_due_task_notification(task_id: str):
    """
    Handles the logic for a single due task, e.g., marking it as notified.

    Args:
        task_id (str): The ID of the task to process.
    """
    from todos.services import task_set_notification_sent

    try:
        task = Task.objects.get(id=task_id)
        task_set_notification_sent(task=task)
        logger.info(f"Notification flag set for task {task_id}")

        # Здесь в будущем будет логика отправки уведомления в Telegram
        # Например, вызов webhook-а или другой механизм.
        # Для текущего задания достаточно просто пометить флаг.

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