import secrets
import math  # Not used in UserViewSet logic directly
import random  # Not used in UserViewSet logic directly
import string  # Not used in UserViewSet logic directly
import os  # For user_avatar_path, ensure it's imported in models.py too
# import logging # No longer needed if all logging calls are removed
from datetime import datetime

from django.conf import settings
from django.db import connections, transaction  # Import transaction
from django.shortcuts import render  # Not typically used in API viewsets
from django.contrib.auth import login, logout  # For session management

from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
# Assuming UserRateThrottle is generic DRF
from rest_framework.throttling import UserRateThrottle
# Correct import from rest_framework.response
from rest_framework.response import Response

# Import your custom modules and models
# Ensure AppUser is imported/defined
from ..models import User, Role, Application, AccessToken

# Serializers
from ..serializers import (
    UserBaseShow,
    UserSerializer, ApplicationSerializer
)
from ..Serializers import UserAuthenticationSerializers

from IT_OAUTH.throttles import *  # Your custom throttle
from ..perms import IsAuthen
# from ..utils.ResponseMessage import BaseDataRespone, MESSAGE, code_info # No longer needed
# from ..logging_ultils import USER_ExcuteLogging_LOGIN_INFO, USER_ExcuteLogging_LOGIN_BUG, LoggingDescription # No longer needed

# logger = logging.getLogger(__name__) # No longer needed

# User


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows applications to be viewed or edited.
    Requires admin privileges.
    """
    queryset = Application.objects.using('oauth').all()
    serializer_class = ApplicationSerializer
    # Only admin users can manage applications
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [SuperRateThrottle]  # Apply your custom throttle

    # Override create to ensure sensitive info is not returned directly if not desired,
    # though with read_only_fields it's generally fine.
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Use Django transaction for atomicity in case of related logic
            with transaction.atomic(using='oauth'):
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)

                return Response({
                    "message": f"Ứng dụng '{serializer.instance.name}' đã được tạo thành công.",
                    # Returns the created application with generated client_id/secret
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            # Log the exception for debugging
            # logger.exception(f"Error creating application: {e}")
            return Response({
                "message": f"Tạo ứng dụng thất bại do lỗi hệ thống: {e}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Lấy thông tin ứng dụng thành công.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "message": "Lấy danh sách ứng dụng thành công.",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "Lấy danh sách ứng dụng thành công.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic(using='oauth'):
                self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly refresh the instance from the database.
                instance = self.get_object()
                serializer = self.get_serializer(instance)

            return Response({
                "message": f"Ứng dụng '{serializer.instance.name}' đã được cập nhật thành công.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # logger.exception(f"Error updating application {instance.id}: {e}")
            return Response({
                "message": f"Cập nhật ứng dụng thất bại do lỗi hệ thống: {e}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        app_name = instance.name
        try:
            with transaction.atomic(using='oauth'):
                self.perform_destroy(instance)
            return Response({
                "message": f"Ứng dụng '{app_name}' đã được xóa thành công."
            }, status=status.HTTP_204_NO_CONTENT)  # 204 No Content for successful deletion
        except Exception as e:
            # logger.exception(f"Error deleting application {instance.id}: {e}")
            return Response({
                "message": f"Xóa ứng dụng thất bại do lỗi hệ thống: {e}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
