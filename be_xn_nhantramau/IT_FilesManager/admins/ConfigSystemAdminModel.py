from django.shortcuts import render
from django.urls import path
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import mark_safe
from django.contrib.auth import authenticate, login
from ..models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.admin import helpers
from IT_OAUTH.admin_base import ConfirmActionAdmin
from django.conf import settings
import base64


# ================= ConfigApp ================= #
class ConfigAppAdminForm(forms.ModelForm):
    class Meta:
        model = ConfigApp
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False


class ConfigAppAdmin(ConfirmActionAdmin):
    form = ConfigAppAdminForm
    # search_fields = ('STT_NGAY', 'ID_DK', 'MABN', 'HOTEN', 'NAMSINH')
    list_display = ["get_list_display"]

    def save_model(self, request, obj, form, change):
        if change:  # If the object is being updated
            # Only save the fields that were changed
            obj.save(update_fields=form.changed_data)
        else:
            # Save the object normally if it's new
            super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        fields = [field.name for field in ConfigApp._meta.get_fields()]
        # Ensure 'id' is the first in the list
        # fields.remove("id")
        return fields
