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

# Message
from general_utils.ResponseMessage import MESSAGE_INSTANCES


logger_user_login = LogHelper("log_user_login_info")
name_title_user_login = "ĐĂNG NHẬP"
# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")


def return_2_seconds_add_token(request):
    # --- SETTING CONFIG --- #
    number_add_time_expired_seconds = 21600  # Default value
    number_add_time_expired_refresh_seconds = 3600

    add_time_config = GET_VALUE_ACTION_SYSTEM(
        ConfigApp, "ACCESS_TOKEN_EXPIRE_SECONDS", "oauth"
    )
    # Check if a value was returned and it's a number
    if add_time_config:
        try:
            # Attempt to convert the string to an integer
            number_add_time_expired_seconds = int(add_time_config)
        except ValueError:
            logger_bug_sys.warning(
                request,
                ResponseBase.STATUS_BAD_REQUEST,
                "LỖI CẤU HÌNH THAM SỐ 'ACCESS_TOKEN_EXPIRE_SECONDS'",
                f"Warning: Configuration for ACCESS_TOKEN_EXPIRE_SECONDS is not a valid number: '{add_time_config}'. Using default value.",
            )
    # -- #
    add_time_refresh_config = GET_VALUE_ACTION_SYSTEM(
        ConfigApp, "ACCESS_TOKEN_EXPIRE_REFRESH_SECONDS", "oauth"
    )
    if add_time_refresh_config:
        try:
            # Attempt to convert the string to an integer
            number_add_time_expired_refresh_seconds = int(add_time_refresh_config)
        except ValueError:
            logger_bug_sys.warning(
                request,
                ResponseBase.STATUS_BAD_REQUEST,
                "LỖI CẤU HÌNH THAM SỐ 'ACCESS_TOKEN_EXPIRE_REFRESH_SECONDS'",
                f"Warning: Configuration for ACCESS_TOKEN_EXPIRE_REFRESH_SECONDS is not a valid number: '{add_time_refresh_config}'. Using default value.",
            )
    # --- SETTING CONFIG --- #
    return number_add_time_expired_seconds, number_add_time_expired_refresh_seconds


# User
class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.using("oauth").all()
    throttle_classes = [SuperRateThrottle]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_serializer_class(self):
        if self.action == "register_user" or self.action == "register_user_by_app":
            return UserAuthenticationSerializers.UserRegistrationSerializer
        elif self.action == "login_user":
            return UserAuthenticationSerializers.UserLoginSerializer
        elif self.action == "current_user":
            return UserBaseShow
        return UserSerializer

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
        url_path="current-user",
        permission_classes=[IsAuthen],
    )
    def current_user(self, request):
        """
        Retrieves details of the currently authenticated user.
        """
        response = ResponseBase()
        try:
            user = request.user
            user.last_login = datetime.now()
            user.save(using="oauth")

            # Direct DRF Response with Vietnamese messages
            response.set_data(UserBaseShow(user).data)
            response.set_status(ResponseBase.STATUS_OK)
            response.set_message(
                MESSAGE_INSTANCES(
                    "SUCCESS_LAY_DU_LIEU_THONG_TIN_NGUOI_HIEN_TAI", request.language
                ).format(username=user.username)
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        except AttributeError:
            response.set_status(ResponseBase.STATUS_UNAUTHORIZED)
            response.set_message(
                MESSAGE_INSTANCES(
                    "FAIL_LAY_DU_LIEU_THONG_TIN_NGUOI_HIEN_TAI", request.language
                )
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
        except Exception as e:
            response.set_data(None)
            response.set_status(ResponseBase.STATUS_INTERNAL_SERVER_ERROR)
            response.set_message(
                MESSAGE_INSTANCES("DEFAULT_FAIL_LOI_HE_THONG", request.language)
            )
            response.add_error(
                {
                    "error": MESSAGE_INSTANCES(
                        "DEFAULT_FAIL_LOI_HE_THONG_KEM_THEO_MESSAGE", request.language
                    ).format(message=str(e)),
                }
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ POST ------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(
        methods=["post"],
        detail=False,
        url_path="register",
        permission_classes=[permissions.AllowAny],
    )
    def register_user(self, request):
        """
        Registers a new user account.
        """
        response = ResponseBase()  # Your custom response object
        data = request.data

        # === THIS IS THE CRITICAL CHANGE ===
        # Create an actual instance of the User model first.
        new_user = User()  # Create the empty User object

        # Then, pass this *instance* (new_user) to the function.
        # DO NOT pass 'User' (the class).
        assign_fields_to_instance(
            instance=new_user,  # <--- THIS MUST BE THE INSTANCE VARIABLE
            data=data,
            # Continue to exclude for manual handling
            exclude_fields=["password", "password2"],
            response=response,
        )
        # Now, 'new_user' object has the fields assigned to it.

        # === END CRITICAL CHANGE ===

        # Handle validation errors collected by assign_fields_to_instance
        if hasattr(response, "list_errors") and response.list_errors:
            if hasattr(response.list_errors, "entities_error") and hasattr(
                response.list_errors, "servers_error"
            ):
                if (
                    response.list_errors["entities_error"]
                    or response.list_errors["servers_error"]
                ):
                    response.set_data = None
                    response.set_message(
                        MESSAGE_INSTANCES(
                            "DEFAULT_FAIL_DU_LIEU_KHONG_HOP_LE", request.language
                        )
                    )
                    response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                    return Response(
                        data=response.return_response()["data_response"],
                        status=response.return_response()["status_response"],
                    )

        # Manual password handling for security
        password = data.get("password")
        password2 = data.get("password2")

        if not password:
            # Add error to response object
            response.add_error(
                {
                    "stt": len(response.list_errors) + 1,
                    "field": "password",
                    "message": "Mật khẩu không được để trống.",
                }
            )

            response.set_data = None
            response.set_message(
                MESSAGE_INSTANCES("FAIL_OAUTH_YEU_CAU_NHAP_MATKHAU", request.language)
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        if password != password2:
            # Add error to response object
            response.add_error(
                {
                    "stt": len(response.list_errors) + 1,
                    "field": "password2",
                    "message": "Mật khẩu xác nhận không khớp.",
                }
            )
            response.set_data = None
            response.set_message(
                MESSAGE_INSTANCES(
                    "FAIL_OAUTH_MATKHAU_XACNHAN_KHONG_KHOP", request.language
                )
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        try:
            # Check for duplicate username/email after basic field assignment
            if User.objects.using("oauth").filter(username=new_user.username).exists():
                response.set_data = None
                response.set_message(
                    MESSAGE_INSTANCES(
                        "FAIL_OAUTH_USERNAME_DA_DUOC_SUDUNG", request.language
                    )
                )
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

            if (
                new_user.email
                and User.objects.using("oauth").filter(email=new_user.email).exists()
            ):
                response.set_data = None
                response.set_message(
                    MESSAGE_INSTANCES(
                        "FAIL_OAUTH_EMAIL_DA_DUOC_SUDUNG", request.language
                    )
                )
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

            new_user.set_password(password)  # Securely hash the password
            new_user.save(using="oauth")

            response.set_data(UserBaseShow(new_user).data)
            response.set_status(ResponseBase.STATUS_CREATED)
            response.set_message(
                MESSAGE_INSTANCES(
                    "SUCCESS_OAUTH_DANGKY_NGUOIDUNG", request.language
                ).format(username=new_user.username)
            )

            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        except Exception as e:
            # IT_OAUTH.. (error handling for database save) IT_OAUTH..
            response.set_data(None)
            response.set_status(ResponseBase.STATUS_INTERNAL_SERVER_ERROR)
            response.set_message(
                MESSAGE_INSTANCES(
                    "DEFAULT_FAIL_LOI_HE_THONG_TAO_DU_LIEU_CHUNG", request.language
                )
            )
            response.add_error(
                {
                    "error": MESSAGE_INSTANCES(
                        "DEFAULT_FAIL_LOI_HE_THONG_TAO_DU_LIEU_KEM_THEO_MESSAGE",
                        request.language,
                    ).format(message=str(e)),
                }
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    @action(
        methods=["post"],
        detail=False,
        url_path="login",
        permission_classes=[permissions.AllowAny],
    )
    def login_user(self, request):
        response = ResponseBase()
        # kiểm tra action
        action = CHECK_ACTION_SYSTEM(ConfigApp, "ACTION_LOGIN", "oauth")
        if action:
            return action

        data_post = request.data.copy()
        data_post.appendlist("language", request.language)
        # truyền body data vào Check Dữ Liệu
        serializer = UserAuthenticationSerializers.UserLoginSerializer(data=data_post)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            # Use .get() to handle the None case gracefully

            application = serializer.validated_data.get("application", None)

            try:
                with transaction.atomic(using="oauth"):
                    # Revoke previous tokens for this user/application pair.
                    # This also works if application is None.
                    if "logout_previous_tokens" in request.data:
                        if request.data["logout_previous_tokens"] == "true":
                            # Revoke all active tokens for this user and application
                            AccessToken.objects.filter(
                                user=user, application=application, active=True
                            ).update(active=False)

                    # Setup seconds
                    number_1, number_2 = return_2_seconds_add_token(request)
                    new_token = AccessToken.objects.create(
                        user=user,
                        application=application,
                        expires_at=timezone.now() + timedelta(seconds=number_1),
                        refresh_expires_at=timezone.now()
                        + timedelta(seconds=(number_1 + number_2)),
                        active=True,
                    )

                    # IT_OAUTH.. (rest of the view logic to return the token) IT_OAUTH..

                    token_serializer = (
                        AccessTokenSerializers.AccessTokenDetailSerializer(new_token)
                    )

                    # data needs to be encoded
                    data_hash = {
                        "token": token_serializer.data,
                        "user": UserBaseShow(user).data,
                    }

                    # # Hash response token
                    # string_response_token = ""
                    # hash_response_token = GET_VALUE_ACTION_SYSTEM(
                    #     ConfigApp, "CONFIG_HASH_RESPONSE_TOKEN_DEFAULT", "oauth"
                    # )

                    # # Make sure the config is a string before using it
                    # if isinstance(hash_response_token, str):
                    #     data_hash_string = json.dumps(data_hash)
                    #     string_response_token = encode_json_with_config(
                    #         data_hash_string, hash_response_token
                    #     )

                    # print(f"string_response_token: {string_response_token}")

                    # Set Data
                    response.set_data(data_hash)
                    response.set_message(
                        MESSAGE_INSTANCES("SUCCESS_DANG_NHAP", request.language)
                    )
                    response.set_status(ResponseBase.STATUS_CREATED)
                    # --- Logging --- #
                    logger_user_login.info(
                        request,
                        200,
                        name_title_user_login,
                        f"- '{user.username}' - đăng nhập thành công!",
                    )
                    # --- Logging --- #
                    return Response(
                        data=response.return_response()["data_response"],
                        status=response.return_response()["status_response"],
                    )

            except Exception as e:
                # Set Data
                response.set_data(None)
                response.set_message(
                    MESSAGE_INSTANCES("FAIL_DANG_NHAP_LOI_HE_THONG", request.language)
                )
                response.add_error({"server": str(e)})
                response.set_status(ResponseBase.STATUS_BAD_GATEWAY)
                # --- Logging --- #
                logger_user_login.info(
                    request,
                    ResponseBase.STATUS_BAD_GATEWAY,
                    name_title_user_login,
                    f"- Đăng nhập không thành công! {str(e)}",
                )
                # --- Logging --- #
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

        else:
            # IT_OAUTH.. (your existing error handling logic) IT_OAUTH..
            # (This part can remain the same, as the serializer handles the validation errors)
            error_message = MESSAGE_INSTANCES(
                "DEFAULT_FAIL_LOI_HE_THONG", request.language
            )
            errors = serializer.errors
            if "non_field_errors" in errors:
                error_detail = errors["non_field_errors"][0]
                if "authorization" in error_detail.code:
                    error_message = error_detail
                elif "inactive" in error_detail.code:
                    error_message = error_detail

            if "client_id" in errors:
                # Use the specific error message from the serializer
                error_message = errors["client_id"][0]

            if "client_secret" in errors:
                # Use the specific error message from the serializer
                error_message = errors["client_secret"][0]

            response.set_message(error_message)
            response.set_status(response.STATUS_UNAUTHORIZED)

            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    @action(
        methods=["post"], detail=False, url_path="logout", permission_classes=[IsAuthen]
    )
    def logout_user(self, request):
        """
        API endpoint for user logout.
        Revokes the access token used for the current request.
        """
        response = ResponseBase()
        # In a token-based system, request.auth contains the token instance
        # that was used for authentication. We must check if it's an AccessToken.
        if (
            request.user.is_authenticated
            and hasattr(request, "auth")
            and isinstance(request.auth, AccessToken)
        ):
            token = request.auth

            # Revoke the token by setting its is_active field to False
            token.active = False
            token = write_log(token, request)
            token.save(update_fields=["active"])

            # Trả
            response.set_data(None)
            response.set_message(
                MESSAGE_INSTANCES("SUCCESS_DANG_XUAT", request.language)
            )
            response.set_status(ResponseBase.STATUS_OK)

            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
        else:
            # This handles cases where no valid token was provided in the first place,
            # or if the user is authenticated via another method (like sessions).
            # Trả
            response.set_data(None)
            response.set_message(
                MESSAGE_INSTANCES(
                    "FAIL_DANG_XUAT_KHONG_CO_PHIEN_DANGNHAP", request.language
                )
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    @action(
        methods=["post"],
        detail=False,
        url_path="refresh-token",
        permission_classes=[permissions.AllowAny],
    )
    def refresh_token(self, request):
        """
        Refreshes an expired access token using a valid refresh token.
        """
        response = ResponseBase()
        serializer = AccessTokenSerializers.TokenRefreshSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Use the validated refresh token from the serializer
                refresh_token_instance = serializer.validated_data["refresh_token"]
                user = refresh_token_instance.user
                application = refresh_token_instance.application

                # Revoke the old refresh token
                with transaction.atomic(using="oauth"):
                    refresh_token_instance.active = False
                    refresh_token_instance.save(update_fields=["active"])

                    # Generate a new access token
                    number_1, number_2 = return_2_seconds_add_token(request)
                    new_token = AccessToken.objects.create(
                        user=user,
                        application=application,
                        expires_at=timezone.now() + timedelta(seconds=number_1),
                        refresh_expires_at=timezone.now()
                        + timedelta(seconds=(number_1 + number_2)),
                    )

                    token_serializer = (
                        AccessTokenSerializers.AccessTokenDetailSerializer(new_token)
                    )
                    user_serializer = UserBaseShow(user)

                    # data needs to be encoded
                    data_hash = {
                        "token": token_serializer.data,
                        "user": user_serializer.data,
                    }

                    # Hash response token
                    string_response_token = ""
                    hash_response_token = GET_VALUE_ACTION_SYSTEM(
                        ConfigApp, "CONFIG_HASH_RESPONSE_TOKEN_DEFAULT", "oauth"
                    )

                    # Make sure the config is a string before using it
                    if isinstance(hash_response_token, str):
                        data_hash_string = json.dumps(data_hash)
                        string_response_token = encode_json_with_config(
                            data_hash_string, hash_response_token
                        )

                    response.set_data(string_response_token)
                    response.set_message(
                        MESSAGE_INSTANCES("SUCCESS_LAMMOI_TOKEN", request.language)
                    )
                    response.set_status(ResponseBase.STATUS_CREATED)

                    return Response(
                        data=response.return_response()["data_response"],
                        status=response.return_response()["status_response"],
                    )

            except Exception as e:
                response.set_data(None)
                response.set_message(
                    MESSAGE_INSTANCES("FAIL_LAMMOI_TOKEN_DO_HE_THONG", request.language)
                )
                response.add_error({"error": str(e)})
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

        else:
            # Handle serializer validation errors
            response.set_data(None)
            response.set_message(
                MESSAGE_INSTANCES("FAIL_LAMMOI_TOKEN", request.language)
            )
            response.add_error({"error": serializer.errors})
            response.set_status(ResponseBase.STATUS_UNAUTHORIZED)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    @action(
        methods=["post"],
        detail=False,
        url_path="change-password",
        permission_classes=[IsAuthen],
    )
    def change_password(self, request):
        """
        Allows an authenticated user to change their password.
        """
        response = ResponseBase()
        user = request.user

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all([old_password, new_password, confirm_password]):
            response.set_data(None)
            response.set_message(
                MESSAGE_INSTANCES("FAIL_DOI_MATKHAU_NHAP_THIEU", request.language)
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        if not user.check_password(old_password):
            response.set_data(None)
            response.set_message(
                MESSAGE_INSTANCES(
                    "FAIL_DOI_MATKHAU_MAT_KHAU_KHONG_CHINH_XAC", request.language
                )
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        if new_password != confirm_password:
            response.set_data(None)
            response.set_message(
                MESSAGE_INSTANCES(
                    "FAIL_DOI_MATKHAU_2_MAT_KHAU_KHONG_KHOP", request.language
                )
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

        try:
            user.set_password(new_password)
            user = write_log(user, request)
            user.save()

            response.set_data(UserBaseShow(user).data)
            response.set_message(
                MESSAGE_INSTANCES("SUCCESS_DOI_MATKHAU", request.language)
            )
            response.set_status(ResponseBase.STATUS_OK)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
        except Exception as e:
            # Consider keeping a basic logging mechanism for unexpected errors
            # print(f"Error changing password for user {user.username}: {e}")
            response.set_data(UserBaseShow(user).data)
            response.set_message(
                MESSAGE_INSTANCES(
                    "DEFAULT_FAIL_LOI_HE_THONG_KEM_THEO_MESSAGE", request.language
                ).format(message=str(e))
            )
            response.set_status(ResponseBase.STATUS_INTERNAL_SERVER_ERROR)
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
