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


from general_utils.models import LogEntrySys, BaseModel as BaseModelGeneral, ConfigSystem, IPManager
# SOCKET_SYS
from IT_SOCKET_SYS.utils.NotifyUtils import send_sync_model_notification


class LogEntryApp(LogEntrySys):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_log_default")

    class Meta:
        verbose_name_plural = "LOG HỆ THỐNG DEFAULT"


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

            # Notify Channel Layer if the model has a channel layer
            send_sync_model_notification(
                model_name=self.__class__.__name__,
                item_id=str(self.pk),
                payload={
                    "action": "log_action",
                    "model_name": self.__class__.__name__,
                    "event": "update",
                    "object_id": str(self.pk),
                    "object_repr": force_str(self),
                })
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


class Dictionary(BaseModel):
    """
    Model for storing key-value pairs for various configurations.
    Inherits from BaseModel to utilize common functionalities.
    """
    key = models.CharField(
        max_length=255,
        verbose_name=_("Key"),
        help_text=_("This dictionary entry.")
    )
    value = models.TextField(
        null=True,
        blank=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of this dictionary entry.")
    )
    type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Type"),
        help_text=_(
            "The type of this dictionary entry (e.g., 'config', 'setting').")
    )
    note = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Note"),
        help_text=_(
            "Any additional notes or comments about this dictionary entry.")
    )
    sort_index = models.SmallIntegerField(
        null=True,
        default=1,
        verbose_name=_("Sort Index"),
        help_text=_("Sort Index")
    )

    class Meta:
        verbose_name_plural = _('Dictionaries')
        ordering = ['key']  # Order entries alphabetically by key

    def __str__(self):
        return f"{self.key}: {self.value}"


# class GhiNhanMauXetNghiem(BaseModel):
#     """
#     Ghi nhận mẫu & trả mẫu
#     """
#     key = models.CharField(
#         max_length=255,
#         verbose_name=_("Key"),
#         help_text=_("This dictionary entry.")
#     )
#     value = models.TextField(
#         null=True,
#         blank=True,
#     )
#     description = models.TextField(
#         null=True,
#         blank=True,
#         verbose_name=_("Description"),
#         help_text=_("A brief description of this dictionary entry.")
#     )
#     type = models.CharField(
#         max_length=255,
#         null=True,
#         blank=True,
#         verbose_name=_("Type"),
#         help_text=_(
#             "The type of this dictionary entry (e.g., 'config', 'setting').")
#     )
#     note = models.TextField(
#         null=True,
#         blank=True,
#         verbose_name=_("Note"),
#         help_text=_(
#             "Any additional notes or comments about this dictionary entry.")
#     )
#     sort_index = models.SmallIntegerField(
#         null=True,
#         default=1,
#         verbose_name=_("Sort Index"),
#         help_text=_("Sort Index")
#     )

#     class Meta:
#         verbose_name_plural = _('Dictionaries')
#         ordering = ['key']  # Order entries alphabetically by key

#     def __str__(self):
#         return f"{self.key}: {self.value}"


class ConfigApp(ConfigSystem):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_config_default")

    class Meta:
        verbose_name_plural = "CÀI ĐẶT APP DEFAULT"
