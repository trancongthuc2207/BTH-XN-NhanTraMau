from django.db import models
from django.utils.encoding import force_str
from django.contrib.admin.models import CHANGE
from django.conf import settings
from datetime import datetime, date
from decimal import Decimal
import json


def is_serializable(value):
    return isinstance(value, (str, int, float, bool, type(None), list, dict))


class LogEntrySys(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_log_sys")
    content_type_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.TextField()
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField(blank=True)
    action_time = models.DateTimeField(auto_now=True)

    # Extra audit fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name_plural = "LOG HỆ THỐNG"

    def __str__(self):
        return f"{self.user} - {self.object_repr} ({self.action_flag})"


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    note_language = models.TextField(null=True, blank=True)

    _modified_by = None
    _ip_address = None
    _session_key = None
    _original_state = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_state = self._as_dict()

    def _as_dict(self):
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, models.Model):
                value = value.pk
            elif not is_serializable(value):
                value = str(value)
            data[field.name] = value
        return data

    def get_changed_fields(self):
        new_state = self._as_dict()
        changed = {}
        for field, original_value in self._original_state.items():
            new_value = new_state.get(field)
            if new_value != original_value:
                changed[field] = {
                    "old": original_value,
                    "new": new_value
                }
        return changed

    @property
    def modified_by(self):
        return self._modified_by

    @modified_by.setter
    def modified_by(self, user):
        self._modified_by = user

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        self._ip_address = ip_address

    @property
    def session_key(self):
        return self._session_key

    @session_key.setter
    def session_key(self, session_key):
        self._session_key = session_key

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super().save(*args, **kwargs)

        changed_fields = self.get_changed_fields()
        self._original_state = self._as_dict()  # reset after save

        if not changed_fields:
            return

        if self._modified_by:
            change_message = json.dumps(changed_fields, ensure_ascii=False)
            self.log_action(self._modified_by, CHANGE, change_message)

    def log_action(self, user, action_flag, change_message):
        LogEntrySys.objects.create(
            user=user,
            content_type_name=self.__class__.__name__,
            object_id=self.pk,
            object_repr=force_str(self),
            action_flag=action_flag,
            change_message=change_message,
            ip_address=self._ip_address,
            session_key=self._session_key,
        )


class ConfigSystem(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, related_name='user_config')
    name_config = models.CharField(max_length=200, null=True)
    value = models.TextField(null=True, default="")
    status = models.BooleanField(null=True, default=False)
    description = models.TextField(null=True, default="")
    position = models.CharField(max_length=200, null=True)
    is_used = models.BooleanField(null=True, default=False)
    type_config = models.CharField(max_length=200, null=True)

    class Meta:
        abstract = True
        verbose_name_plural = "CÀI ĐẶT HỆ THỐNG"  # Plural name

    def __str__(self):
        return f"{self.name_config}"


class IPManager(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_ip")
    ip = models.CharField(max_length=256, null=True)
    path = models.TextField(null=True, default="")
    request = models.TextField(null=True, default="")
    time_expired = models.DateTimeField(null=True)
    error_name = models.CharField(max_length=256, null=True)

    class Meta:
        abstract = True
        verbose_name_plural = "QUẢN LÝ IP"  # Plural name

    def __str__(self):
        return f"{self.ip}"
