from django.db import models
from IT_OAUTH.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.encoding import force_str
from django.conf import settings
import json
from datetime import datetime, timezone
import uuid
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import base64
import os
import mimetypes
from django.utils.translation import gettext_lazy as _

# general_utils
from general_utils.models import LogEntrySys, BaseModel as BaseModelGeneral, ConfigSystem, IPManager
from general_utils.utils import extract_template_variables


class LogEntryApp(LogEntrySys):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_log_mail")

    class Meta:
        verbose_name_plural = "LOG HỆ THỐNG FILE"


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


class FormMail(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_mail_form")
    name_form = models.CharField(max_length=256, null=True, blank=True)
    name_subject_mail = models.TextField(
        verbose_name=_("name_subject_mail"),
        null=True,
        blank=True,
    )
    value = models.TextField(null=True, blank=True, default="")
    default_variables = models.TextField(null=True, blank=True)
    is_used = models.BooleanField(null=True, blank=True, default=False)
    type_form = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name_form or f"FormMail {self.pk}"

    def save(self, *args, **kwargs):
        # A simple check to ensure recipient_list is a valid JSON string
        self.default_variables = json.dumps(
            extract_template_variables(self.value), ensure_ascii=False)
        super().save(*args, **kwargs)


class HistorySendMail(BaseModel):
    # A list of possible statuses for the email
    STATUS_CHOICES = (
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        help_text="The user who initiated the email, or None for system emails.", related_name="user_send_mail"
    )
    recipient_list = models.TextField(
        help_text="JSON array of email recipients."
    )
    subject = models.CharField(
        max_length=500,
        help_text="The subject line of the email."
    )
    body = models.TextField(
        help_text="The body of the email (can be HTML)."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="The sending status of the email."
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Details of any error that occurred during sending."
    )

    class Meta:
        verbose_name = "Email History"
        verbose_name_plural = "Email Histories"
        ordering = ['-created_date']

    def __str__(self):
        return f"Email to {self.recipient_list} - Status: {self.status}"

    def save(self, *args, **kwargs):
        # A simple check to ensure recipient_list is a valid JSON string
        if isinstance(self.recipient_list, list):
            self.recipient_list = json.dumps(
                self.recipient_list, ensure_ascii=False)
        super().save(*args, **kwargs)


class BackgroundTask(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    command_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50, default="PENDING"
    )  # PENDING, RUNNING, COMPLETED, FAILED
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "LỊCH SỬ THỰC THI COMMAND"  # Plural name


class ConfigApp(ConfigSystem):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_mail")

    class Meta:
        verbose_name_plural = "CÀI ĐẶT APP MAILMANAGER"
