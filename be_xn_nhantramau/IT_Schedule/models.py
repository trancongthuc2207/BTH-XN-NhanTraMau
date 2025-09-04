from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.encoding import force_str
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.exceptions import ValidationError

# general_utils
from general_utils.models import LogEntrySys, BaseModel as BaseModelGeneral, ConfigSystem, IPManager


class LogEntryApp(LogEntrySys):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_schedule")

    class Meta:
        verbose_name_plural = "LOG HỆ THỐNG SCHEDULE"


class BaseModel(BaseModelGeneral):
    class Meta:
        abstract = True
        ordering = ['-created_date']

    def save(self, *args, **kwargs):
        if self.pk:  # If the instance already exists, compare changes
            old_instance = self.__class__.objects.filter(pk=self.pk).first()
            if old_instance:
                changed_fields = {}
                for field in self._meta.fields:
                    old_value = getattr(old_instance, field.name)
                    new_value = getattr(self, field.name)

                    # If the field is a foreign key, compare by ID
                    if isinstance(field, models.ForeignKey):
                        old_value = old_value.pk if old_value else None
                        new_value = new_value.pk if new_value else None

                    # If the old or new value is a datetime, convert it to string
                    if isinstance(old_value, datetime):
                        old_value = old_value.strftime("%Y-%m-%d %H:%M:%S.%f")
                    if isinstance(new_value, datetime):
                        new_value = new_value.strftime("%Y-%m-%d %H:%M:%S.%f")

                    # Handle ImageField and FileField
                    if isinstance(field, models.ImageField) or isinstance(
                        field, models.FileField
                    ):
                        old_value = old_value.name if old_value else None
                        new_value = new_value.name if new_value else None

                    # 🔹 Fix: Handle float precision issues
                    if isinstance(old_value, float) or isinstance(old_value, Decimal):
                        # Convert to string with 6 decimal places
                        old_value = f"{old_value:.6f}"
                    if isinstance(new_value, float) or isinstance(new_value, Decimal):
                        new_value = f"{new_value:.6f}"

                    if old_value != new_value:
                        changed_fields[field.name] = {
                            "old": old_value,
                            "new": new_value,
                        }

                # if changed_fields and self.modified_by:
                if changed_fields:
                    change_message = json.dumps(
                        [{"changed": changed_fields}], ensure_ascii=False)
                    self.log_action(self.modified_by, CHANGE, change_message)
        else:
            # Optionally log creation (ADDITION) here if needed
            pass
        super().save(*args, **kwargs)

    def log_action(self, user, action_flag, change_message):
        LogEntryApp.objects.create(
            user=user,
            content_type_name=self.__class__.__name__,
            object_id=self.pk,
            object_repr=force_str(self),
            action_flag=action_flag,
            change_message=change_message,
            ip_address=self._ip_address,
            session_key=self._session_key,
        )


class Task(BaseModel):
    """
    Represents a function or command to be executed.
    This model defines 'what' to run.
    """
    name = models.CharField(max_length=255, unique=True,
                            help_text="A unique, descriptive name for the task.")
    description = models.TextField(
        blank=True, null=True, help_text="Detailed description of what this task does.")
    file_path = models.CharField(
        max_length=255,
        help_text="Relative path to the Python file, e.g., 'tasks.general_tasks'."
    )
    function_name = models.CharField(
        max_length=100,
        help_text="Name of the function to be executed within the specified file."
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "ĐỊNH NGHĨA TÁC VỤ"
        ordering = ['name']


class Schedule(BaseModel):
    """
    Represents a schedule for a specific Task.
    This model defines 'when' to run a task.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        related_name='schedules',
        help_text="Select the task to be scheduled.",
        null=True
    )

    # Use either cron_schedule or interval_minutes, but not both.
    cron_schedule = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="""
        [ '*/5 * * * *' => Every 5 minutes ]  
        [ '0 * * * *' => Every hour, at minute 0 ]  
        [ '30 14 * * *' => Every day at 14:30 (2:30 PM) ]  
        [ '0 9 * * 1-5' => Monday to Friday at 9:00 AM ]  
        [ '0 0 * * 0' => Every Sunday at midnight (00:00) ]  
        """
    )
    interval_minutes = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Run every X minutes (ignored if cron is set)."
    )

    # These fields are updated by the scheduler and should not be editable manually
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending', editable=False)
    last_run = models.DateTimeField(blank=True, null=True, editable=False)

    def clean(self):
        """
        Custom validation to ensure either cron_schedule or interval_minutes is set,
        but not both.
        """
        if self.cron_schedule and self.interval_minutes:
            raise ValidationError(
                "You cannot set both a cron schedule and an interval. Please choose one.")
        if not self.cron_schedule and not self.interval_minutes:
            raise ValidationError(
                "You must set either a cron schedule or an interval for the schedule.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Schedule for {self.task.name}"

    class Meta:
        verbose_name_plural = "LỊCH TRÌNH CÔNG VIỆC TỰ ĐỘNG"
        ordering = ['task__name']


class TaskLog(BaseModel):
    """
    Log of each execution of a ScheduledTask.
    """
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.SET_NULL,
        related_name='logs_schedule',
        null=True
    )

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(
        null=True, blank=True, help_text="Duration in milliseconds")

    status = models.CharField(max_length=10, null=True, blank=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Log for '{self.schedule.task.name}' on {self.created_date.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name_plural = "LỊCH SỬ CHẠY TÁC VỤ"
        ordering = ['-created_date']


class ConfigApp(ConfigSystem):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_schedule_setting")

    class Meta:
        verbose_name_plural = "CÀI ĐẶT APP SCHEDULE"
