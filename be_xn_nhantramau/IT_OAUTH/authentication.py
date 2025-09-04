# accounts/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from IT_OAUTH.models import AccessToken, ConfigApp  # Your AccessToken model
from django.http import JsonResponse

#
from rest_framework.response import Response
from rest_framework import status


# Utils
from general_utils.Logging.logging_tools import LogHelper
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.GetConfig.UtilsConfigSystem import (
    GET_VALUE_ACTION_SYSTEM,
    GET_VALUE_BASE64_ACTION_SYSTEM,
    CHECK_ACTION_SYSTEM,
    BOOL_CHECK_ACTION_SYSTEM,
)


# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")


class OAuth2DRFAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Response
        response = ResponseBase()
        #
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        key_prefix = "Bearer"
        key_prefix_config = GET_VALUE_ACTION_SYSTEM(
            ConfigApp, "KEY_AUTHORIZATION", "oauth"
        )
        # Check if a value was returned and it's a number
        if key_prefix_config:
            try:
                # Attempt to convert the string to an integer
                key_prefix = key_prefix_config
            except ValueError:
                logger_bug_sys.warning(
                    request,
                    ResponseBase.STATUS_BAD_REQUEST,
                    "LỖI CẤU HÌNH THAM SỐ 'KEY_AUTHORIZATION'",
                    f"Warning: Configuration for KEY_AUTHORIZATION is not a valid: '{key_prefix_config}'. Using default value.",
                )

        if not auth_header or not auth_header.startswith(f"{key_prefix} "):
            logger_bug_sys.warning(
                request,
                ResponseBase.STATUS_BAD_REQUEST,
                "CLIENT SEND 'KEY_AUTHORIZATION' SAI!",
                f"Yêu cầu sử dụng KEY: '{key_prefix}'",
            )
            return None  # No Bearer token, let other authentication classes handle or remain anonymous

        token_value = auth_header.split(" ")[1]
        try:
            # Cập nhật
            access_token = AccessToken.objects.select_related("user").get(
                access_token=token_value
            )
            if not access_token.user.is_superuser:
                if access_token.application is None:
                    raise ValueError(
                        "#99#: Token không hợp lệ hoặc đã bị xóa.")
                if access_token.application.active == False:
                    raise ValueError("#99#: Token không còn hoạt động.")

            if access_token.active == False:
                raise ValueError("#00#: Token đã bị vô hiệu hóa.")
            if access_token.expires_at <= timezone.now():
                access_token.active = False
                access_token.save()
                raise ValueError("#01#: Token đã hết hạn.")

            # authenticate method returns a tuple: (user, auth)
            # auth is typically the token object itself or None
            return (access_token.user, access_token)
        except ValueError as e:
            raise AuthenticationFailed(str(e))
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed(f"#02#: Không tìm thấy token.")
        except Exception as e:
            raise AuthenticationFailed(f"#03#: Lỗi hệ thống!")

    def authenticate_header(self, request):
        """
        Returns a string to be used as the value of the WWW-Authenticate header in a 401 response.
        """
        return 'Bearer realm="api"'
