import threading
from django.utils import timezone
from django.core.management import call_command
from django.db import close_old_connections
from ...models import BackgroundTask  # Adjust the import as needed


def run_command_in_background(command_name, *args, **kwargs):
    # Create a background task record
    task = BackgroundTask.objects.create(
        command_name=command_name, status="PENDING")

    def task_function():
        try:
            close_old_connections()  # Avoid DB connection leaks

            # Update task status to RUNNING
            task.status = "RUNNING"
            task.started_at = timezone.now()
            task.save()

            # Run the command
            try:
                call_command(command_name, *args, **kwargs)
                task.status = "COMPLETED"
                task.finished_at = timezone.now()
            except Exception as e:
                task.status = "FAILED"
                task.result = str(e)

        finally:
            task.save()
            close_old_connections()

    # Run the task in a new thread
    thread = threading.Thread(target=task_function, daemon=True)
    thread.start()

    return task.task_id  # Return the task ID to track later
