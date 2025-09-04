from django.db import models
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


from general_utils.models import LogEntrySys, BaseModel as BaseModelGeneral, ConfigSystem, IPManager


class LogEntryApp(LogEntrySys):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_log_socket")

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


class WebSocketLog(BaseModel):
    """
    A model to log all messages sent and received over WebSocket connections.
    """
    # Unique identifier for the WebSocket connection.
    # This helps group related messages together.
    # For a user, it could be the channel name or a session ID.
    connection_id = models.CharField(
        max_length=255, db_index=True, help_text="A unique identifier for the WebSocket connection.")

    # The user associated with the connection, if authenticated.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The authenticated user associated with this message."
    )

    # The type of message: 'sent' or 'received'.
    message_direction = models.CharField(
        max_length=10,
        choices=[('sent', 'Sent'), ('received', 'Received')],
        help_text="Indicates if the message was sent by the server or received from a client."
    )

    # The name of the group the message was sent to or received from.
    group_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="The name of the Channels group this message is related to."
    )

    # The full JSON payload of the message.
    payload = models.JSONField(help_text="The JSON payload of the message.")

    # The timestamp of when the message was logged.
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "WebSocket Log"
        verbose_name_plural = "WebSocket Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.message_direction.upper()} on {self.group_name or 'N/A'}"


class ConfigApp(ConfigSystem):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_app_socket")

    class Meta:
        verbose_name_plural = "CÀI ĐẶT APP SOCKET"
