from rest_framework import serializers
# Ensure all necessary models are imported
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
# --- Existing Serializers (for context) ---
from IT_FilesManager.models import *
from IT_FilesManager.serializers import FileInformationSerializer, FileTypeSerializer


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = [
            field.name  # Use field.name to get the name of the field
            for field in Files._meta.get_fields()
            if field.name not in ["paymentrequest", "fileinformation"]
        ]
        read_only_fields = fields


class FilesFull_InforSerializer(serializers.ModelSerializer):
    category_infor_FR = serializers.SerializerMethodField()
    file_type_infor_FR = serializers.SerializerMethodField()
    file_information_FR = serializers.SerializerMethodField()

    def get_category_infor_FR(self, Files):
        data = []
        if Files.category:
            try:
                list_category_infor = FileCategory.objects.using("default").filter(
                    pk=Files.category.pk
                )
                data = FileTypeSerializer(
                    list_category_infor, many=True).data
            except Exception as e:
                data = None
        return data

    def get_file_type_infor_FR(self, Files):
        data = []
        if Files.file_type:
            try:
                list_files_type_infor = FileType.objects.using("default").filter(
                    pk=Files.file_type.pk
                )
                data = FileTypeSerializer(
                    list_files_type_infor, many=True).data
            except Exception as e:
                data = None
        return data

    def get_file_information_FR(self, Files):
        data = []
        if Files:
            try:
                list_files_infor = FileInformation.objects.using("default").filter(
                    file=Files, active=True
                )
                data = FileInformationSerializer(
                    list_files_infor, many=True).data
            except Exception as e:
                data = None
        return data

    class Meta:
        model = Files
        fields = [
            field.name  # Use field.name to get the name of the field
            for field in Files._meta.get_fields()
            if field.name not in ["paymentrequest", "fileinformation"]
        ] + ["file_information_FR", "file_type_infor_FR", "category_infor_FR"]
        read_only_fields = fields


class FilesCombineInforSerializer(serializers.ModelSerializer):
    file_information_FR = serializers.SerializerMethodField()

    def get_file_information_FR(self, Files):
        data = []
        if Files:
            try:
                list_files_infor = FileInformation.objects.using("default").filter(
                    file=Files, active=True
                )
                data = FileInformationSerializer(
                    list_files_infor, many=True).data
            except Exception as e:
                data = None
        return data

    class Meta:
        model = Files
        fields = [
            field.name  # Use field.name to get the name of the field
            for field in Files._meta.get_fields()
            if field.name not in ["paymentrequest", "fileinformation"]
        ] + ["file_information_FR"]
        read_only_fields = fields
