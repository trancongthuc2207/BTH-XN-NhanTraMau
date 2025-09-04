import atexit
import logging
import time
import importlib.util
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.utils.timezone import now
from django.apps import apps

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SchedulerManager:
    """
    Manages the lifecycle and tasks of the APScheduler background scheduler.
    This class handles dynamic loading and execution of tasks from specified files.
    """

    def __init__(self):
        self.scheduler = None

    def _dynamic_import_and_get_function(self, file_path, function_name):
        """
        Dynamically imports a module from a given file path and returns a function.
        This allows executing functions from any .py file in the project.
        """
        try:
            # Check if the module is already loaded to avoid re-importing
            if file_path in sys.modules:
                module = sys.modules[file_path]
            else:
                # Use importlib to load the module spec from the file path
                spec = importlib.util.find_spec(file_path)
                if spec is None:
                    raise ImportError(f"Module '{file_path}' not found.")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[file_path] = module

            # Get the function from the loaded module
            func = getattr(module, function_name, None)
            if not callable(func):
                raise AttributeError(
                    f"Function '{function_name}' not found or is not callable.")

            return func
        except (ImportError, AttributeError, Exception) as e:
            logger.error(
                f"❌ Failed to import or find function '{function_name}' from '{file_path}': {e}")
            return None

    def run_scheduled_task(self, schedule_id):
        """
        Executes a single scheduled task. This method is called by the
        scheduler when a job is triggered.
        """
        log_entry = None
        try:
            # Safely get the models from the app registry to avoid circular imports.
            Schedule = apps.get_model('IT_Schedule', 'Schedule')
            TaskLog = apps.get_model('IT_Schedule', 'TaskLog')
            schedule = Schedule.objects.select_related(
                'task').get(id=schedule_id)
            task = schedule.task
        except (Schedule.DoesNotExist, AttributeError):
            logger.error(
                f"❌ Scheduled with ID {schedule_id} or its associated task not found.")
            return

        logger.info(
            f"⚡ Running task: '{task.name}' ({task.file_path}.{task.function_name})")

        try:
            # Update the task status to 'running'
            schedule.status = "running"
            schedule.save()
            start_time = time.time()
            # Create the log entry after we've successfully found the schedule
            log_entry = TaskLog.objects.create(
                schedule=schedule,
                start_time=now(),
                status="running"
            )

            # Dynamically import and run the function
            func_to_run = self._dynamic_import_and_get_function(
                task.file_path, task.function_name)

            if func_to_run:
                func_to_run()
                log_entry.status = "success"
                log_entry.message = "Task completed successfully."
                logger.info(f"✅ Task '{task.name}' completed successfully.")
            else:
                log_entry.status = "failed"
                log_entry.message = f"Error: Function not found or is not callable."
                logger.error(
                    f"❌ Task '{task.name}' failed because the function could not be loaded.")

        except Exception as e:
            # Handle any exceptions that occur during task execution
            if log_entry:
                log_entry.status = "failed"
                log_entry.message = f"Task failed with an unexpected exception: {e}"
            else:
                # In case an exception happens before log_entry is created
                logger.error(
                    f"❌ Failed to create log entry for task '{task.name}' due to exception: {e}", exc_info=True)
            # Use exc_info=True to log the full traceback for debugging
            logger.error(
                f"❌ Task '{task.name}' failed with an exception: {e}", exc_info=True)
        finally:
            if log_entry:
                # Always update the log with end time and duration, then save once
                log_entry.end_time = now()
                log_entry.duration_ms = int((time.time() - start_time) * 1000)
                log_entry.save()

            # Update the schedule's last_run and status
            schedule.last_run = now()
            schedule.status = log_entry.status if log_entry else "failed"
            schedule.save()

    def schedule_all_tasks(self):
        """
        Fetches all active schedules from the database and adds them to the scheduler.
        """
        if not self.scheduler:
            logger.error("Scheduler is not running. Cannot schedule tasks.")
            return

        # Remove all existing jobs before adding new ones
        for job in self.scheduler.get_jobs():
            self.scheduler.remove_job(job.id)
        print("Cleared all existing jobs from the scheduler.")

        Schedule = apps.get_model('IT_Schedule', 'Schedule')
        # Here we use 'active' instead of 'is_allowed_run' based on your previous models.py update.
        schedules = Schedule.objects.filter(active=True).select_related('task')
        if not schedules:
            logger.info("No active schedules found.")
            return

        for schedule in schedules:
            job_id = str(schedule.id)
            if schedule.cron_schedule:
                logger.info(
                    f"Scheduling cron job for task '{schedule.task.name}' with schedule: '{schedule.cron_schedule}'")
                self.scheduler.add_job(
                    self.run_scheduled_task,
                    CronTrigger.from_crontab(schedule.cron_schedule),
                    args=[schedule.id],
                    id=job_id,
                    replace_existing=True
                )
            elif schedule.interval_minutes:
                logger.info(
                    f"Scheduling interval job for task '{schedule.task.name}' with interval: {schedule.interval_minutes} minutes")
                self.scheduler.add_job(
                    self.run_scheduled_task,
                    IntervalTrigger(minutes=schedule.interval_minutes),
                    args=[schedule.id],
                    id=job_id,
                    replace_existing=True
                )
        logger.info(
            f"✅ All {len(schedules)} active schedules have been configured.")

    def start(self):
        """
        Starts the scheduler in the background if it's not already running.
        """
        # Check if the scheduler is already running to avoid restarting
        if self.scheduler and self.scheduler.running:
            logger.info("APScheduler is already running.")
            return

        # 1. Create a BackgroundScheduler instance.
        self.scheduler = BackgroundScheduler()
        print("✅ Created APScheduler instance.")

        # 2. Add all tasks from the database to the newly created scheduler.
        self.schedule_all_tasks()
        print("✅ All tasks have been scheduled.")

        # 3. Start the scheduler to begin running jobs.
        self.scheduler.start()
        print("✅ APScheduler started successfully!")

        # Register a function to shut down the scheduler when the app exits
        atexit.register(lambda: self.scheduler.shutdown(wait=False))

    def reload_schedules(self):
        """
        Reloads all schedules by clearing existing jobs and adding them again.
        This is called when a schedule is updated or deleted via the admin panel.
        """
        logger.info("🔄 Reloading all scheduled jobs due to a change.")
        self.schedule_all_tasks()


# Create a single instance of the manager to be used throughout the application
scheduler_manager = SchedulerManager()
