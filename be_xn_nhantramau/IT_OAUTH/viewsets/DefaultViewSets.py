import secrets
import math  # Not used in UserViewSet logic directly
import random  # Not used in UserViewSet logic directly
import string  # Not used in UserViewSet logic directly
import os  # For user_avatar_path, ensure it's imported in models.py too
import json

# import logging # No longer needed if all logging calls are removed
from datetime import datetime, timedelta
from django.utils import timezone

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
from IT_OAUTH.models import User, Role, Application, AccessToken, ConfigApp
from IT_OAUTH.serializers import UserBaseShow, UserSerializer

# Serializers
from IT_OAUTH.Serializers import UserAuthenticationSerializers
from IT_OAUTH.Serializers import AccessTokenSerializers

from IT_OAUTH.throttles import *  # Your custom throttle
from IT_OAUTH.perms import IsAuthen

# Utils
from general_utils.utils import (
    build_advanced_filters_and_pagination,
    assign_fields_to_instance,
)
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.GetConfig.UtilsAuthen import (
    encode_json_with_config,
    decode_json_with_config,
)
from general_utils.GetConfig.UtilsConfigSystem import (
    GET_VALUE_ACTION_SYSTEM,
    GET_VALUE_BASE64_ACTION_SYSTEM,
    CHECK_ACTION_SYSTEM,
    BOOL_CHECK_ACTION_SYSTEM,
)
from general_utils.Logging.logging_tools import LogHelper
from general_utils.utils import write_log


logger_user_login = LogHelper("log_user_login_info")
name_title_user_login = "ĐĂNG NHẬP"
# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")


# Default
class DefaultViewSetBase(viewsets.ViewSet):
    queryset = User.objects.using("oauth").all()
    throttle_classes = [SuperRateThrottle]
    parser_classes = [parsers.MultiPartParser,
                      parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ["current_user", "logout_user", "change_password"]:
            return [IsAuthen()]
        elif self.action in ["register_user", "login_user"]:
            return [permissions.AllowAny()]
        elif self.action == "register_user_by_app":
            return [IsAuthen()]
        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(
        methods=["get"],
        detail=False,
        url_path="test-api",
        permission_classes=[],
    )
    def page_api_test(self, request):
        """
        This function renders an HTML template. It's the most common way to build a
        web page with Django. We can also pass data to the template.
        """
        # We define a dictionary called 'context' to pass data to the template.
        context = {
            'page_title': "My Django Home Page",
            'message': "Welcome to this fantastic Django website!",
            'items': ['Item A', 'Item B', 'Item C']
        }
        # The render() function takes the request, the template path, and the context dictionary.
        return render(request, 'Test/API_TEST.html', context)

    @action(
        methods=["get"],
        detail=False,
        url_path="test-upload",
        permission_classes=[],
    )
    def page_test_upload(self, request):
        """
        This function renders an HTML template. It's the most common way to build a
        web page with Django. We can also pass data to the template.
        """
        # We define a dictionary called 'context' to pass data to the template.
        context = {
            'page_title': "My Django Home Page",
            'message': "Welcome to this fantastic Django website!",
            'items': ['Item A', 'Item B', 'Item C']
        }
        # The render() function takes the request, the template path, and the context dictionary.
        return render(request, 'Test/TEST_UPLOAD.html', context)

    @action(
        methods=["get"],
        detail=False,
        url_path="test-upload-multi",
        permission_classes=[],
    )
    def page_test_upload_multi(self, request):
        """
        This function renders an HTML template. It's the most common way to build a
        web page with Django. We can also pass data to the template.
        """
        # We define a dictionary called 'context' to pass data to the template.
        context = {
            'page_title': "My Django Home Page",
            'message': "Welcome to this fantastic Django website!",
            'items': ['Item A', 'Item B', 'Item C']
        }
        # The render() function takes the request, the template path, and the context dictionary.
        return render(request, 'Test/TEST_UPLOAD_MULTI.html', context)
