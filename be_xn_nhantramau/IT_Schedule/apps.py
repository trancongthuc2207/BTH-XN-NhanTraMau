from django.apps import AppConfig
from django.db.utils import OperationalError
import logging
import os

logger = logging.getLogger(__name__)


class ItScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'IT_Schedule'

    def ready(self):
        """
        This method is called when the application registry is fully populated.
        It's the perfect place to start the scheduler.
        """
        # We import here to avoid circular imports during startup
        from IT_Schedule.schedule_manager import scheduler_manager

        # Check if the process is the main one before starting the scheduler
        if os.environ.get('RUN_MAIN'):
            try:
                scheduler_manager.start()
                print("--- Scheduler started successfully from IT_Schedule app config.")
            except OperationalError:
                print(
                    "Database not ready. Skipping scheduler start for now.")
            except Exception as e:
                print(f"Failed to start the scheduler: {e}")
        else:
            print("--- Scheduler is not in the main process. Skipping startup.")
