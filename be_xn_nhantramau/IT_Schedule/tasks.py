import logging
from django.conf import settings
from .models import TaskLog

# Configure logging for this module
logger = logging.getLogger(__name__)


def simple_task():
    """
    A basic scheduled task that logs a success message.
    This is useful for testing the scheduler's functionality.
    """
    print("Executing simple_task: This is a message from a scheduled task.")


def task_with_error():
    """
    This task is designed to fail, demonstrating how the system handles errors.
    The TaskLog will capture the exception and mark the task as a failure.
    """
    logger.info("Executing task_with_error: This task will intentionally fail.")
    try:
        # Intentional error to demonstrate logging and error handling
        result = 1 / 0
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.error(f"Error in task_with_error: {e}")
        # Log the failure to the TaskLog model
        TaskLog.objects.create(status='Failure', message=str(e))
        # Re-raise the exception to be caught by the scheduler manager
        raise


def periodic_cleanup_task():
    """
    A more practical task that simulates a periodic cleanup operation.
    It can be configured to run daily, weekly, or monthly.
    """
    logger.info("Executing periodic_cleanup_task: Running database cleanup.")
    # Here you would add your actual cleanup logic, for example:
    # 1. Delete old temporary files
    # 2. Archive outdated database records
    # 3. Optimize database tables
    TaskLog.objects.create(
        status='Success', message="Periodic cleanup completed.")
    logger.info("Periodic cleanup completed.")
