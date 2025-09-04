from rest_framework import serializers
# Ensure all necessary models are imported
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
# --- Existing Serializers (for context) ---
from IT_MailManager.models import *

# general_utils
from general_utils.utils import *


class FormMailSerializer(serializers.ModelSerializer):
    varriables_CUS = serializers.SerializerMethodField()

    def get_varriables_CUS(self, Files):
        data = []
        if Files.value:
            try:
                data = extract_template_variables(Files.value)
            except Exception as e:
                data = None
        return data

    class Meta:
        model = FormMail
        fields = [
            field.name  # Use field.name to get the name of the field
            for field in FormMail._meta.get_fields()
            if field.name not in ["paymentrequest", "fileinformation"]
        ] + ["varriables_CUS"]
        read_only_fields = fields
