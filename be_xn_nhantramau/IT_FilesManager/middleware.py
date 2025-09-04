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

# Config
from IT_OAUTH.models import ConfigApp as ConfigAppOAuth

# Authentication
from IT_OAUTH.authentication import OAuth2DRFAuthentication

# Utils
from general_utils.GetConfig import UtilsAuthen
from general_utils.GetConfig.UtilsConfigSystem import GET_VALUE_ACTION_SYSTEM, GET_VALUE_ACTION_SYSTEM, CHECK_ACTION_SYSTEM, BOOL_CHECK_ACTION_SYSTEM

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")


# Bảo vệ view file
class DynamicProtectedFileMiddleware(MiddlewareMixin):
    """
    Middleware that dynamically checks the password for any file served 
    from MEDIA_URL if it has a corresponding entry in the Files model.
    """

    def process_request(self, request):
        prefix = "pbkdf2_sha256$0e0ac3288f01261829d359a3b3c58dc2$"
        if GET_VALUE_ACTION_SYSTEM(
            ConfigAppOAuth, "PREFIX_CHECK_FILE_DEFAULT", dbname="oauth"
        ):
            prefix = GET_VALUE_ACTION_SYSTEM(
                ConfigAppOAuth, "PREFIX_CHECK_FILE_DEFAULT", dbname="oauth"
            )
        # Check if the request path is for a media file
        if request.path.startswith(settings.MEDIA_URL):
            # Extract the relative path of the file from the URL
            # Example: "/media/uploaded_files/test/file.mp4" -> "uploaded_files/test/file.mp4"
            relative_file_path = request.path[len(settings.MEDIA_URL):]

            provided_password = request.GET.get('file_password', "")

            try:
                decode_password = decode_with_prefix(
                    encoded_string=provided_password, prefix=prefix)
                # Query the database to find the file instance using its relative path
                file_instance = Files.objects.get(
                    file__iexact=relative_file_path)

                # ----- Kiểm tra FILES ----- #
                if file_instance.required_authen:
                    try:
                        UtilsAuthen.CHECK_REQUIRED_AUTHEN_OF_REQUEST(request)
                    except Exception as e:
                        logger_bug_sys.warning(request, 400, "TRUY CẬP FILE",
                                               f"Error processing protected file request: {e}")
                        return HttpResponseForbidden(str(e))

                # Kiểm tra nếu mật khẩu trống
                if not file_instance.password:
                    return None

                # Check the provided password against the stored password hash
                if check_password_hash(decode_password, file_instance.password):
                    # Construct the absolute path to the file on the server
                    file_path = file_instance.file.path
                    if os.path.exists(file_path):
                        return FileResponse(open(file_path, 'rb'))
                    else:
                        logger_bug_sys.warning(request, 400, "TRUY CẬP FILE",
                                               f"Protected file not found on disk: {file_path}")
                        return HttpResponseForbidden("File not found on server.")
                else:
                    logger_bug_sys.warning(request, 400, "TRUY CẬP FILE",
                                           f"Unauthorized access attempt for {relative_file_path} from {request.META.get('REMOTE_ADDR')}")
                    return HttpResponseForbidden("Incorrect password.")

            except Files.DoesNotExist:
                # The file is in the MEDIA_URL, but no entry exists in the Files model,
                # so it's not a protected file. Let the request proceed normally.
                return None
            except Exception as e:
                logger_bug_sys.warning(request, 400, "TRUY CẬP FILE",
                                       f"Error processing protected file request: {e}")
                return HttpResponseForbidden("An internal error occurred.")

        return None
