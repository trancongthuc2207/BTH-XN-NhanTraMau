# your_app/middleware.py

import os
from django.conf import settings
from django.http import FileResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
import logging
from django.db import models
from django.contrib.auth.models import AnonymousUser
# Import your Files model
from IT_FilesManager.models import Files
# Import your password utility functions
from general_utils.utils import check_password_hash, decode_with_prefix
from general_utils.Logging.logging_tools import LogHelper

# Authentication
from IT_OAUTH.authentication import OAuth2DRFAuthentication

# Utils
from general_utils.GetConfig import UtilsAuthen

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")

# Bảo vệ view file


class MailMiddleware(MiddlewareMixin):
    """
    Middleware to protect file access based on user authentication and permissions.
    """

    def process_request(self, request):

        return None
