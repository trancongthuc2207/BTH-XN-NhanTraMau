from rest_framework import serializers
# Ensure all necessary models are imported
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
# --- Existing Serializers (for context) ---
from IT_FilesManager.models import FileType


class FileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileType
        fields = [
            field.name  # Use field.name to get the name of the field
            for field in FileType._meta.get_fields()
            if field.name not in ["paymentrequest"]
        ]
        read_only_fields = fields
