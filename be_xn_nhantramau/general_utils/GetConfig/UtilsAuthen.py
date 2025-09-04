import re
import base64
import json
import mimetypes
from typing import Dict, List, Any
from django.utils import timezone
from django.db.models import Q

# AUTHEN
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# ConfigApp of OAUTH
from IT_OAUTH.models import ConfigApp, AccessToken

# Utils
from general_utils.banking import VietQRGenerator
from general_utils.utils import *
from general_utils.Logging.logging_tools import LogHelper, LogHelperOnlyString
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

# Logger sys
logger_bug_string_socket = LogHelperOnlyString("log_socket_bug")

# ---------------------------- #
# ---------------------------- #
# ---------- CHECK ----------- #
# ---------------------------- #
# ---------------------------- #


def CHECK_REQUIRED_AUTHEN_OF_REQUEST(request):
    # Response
    response = ResponseBase()
    #
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")

    if not auth_header:
        raise ValueError("#99#: Yêu cầu đăng nhập.")

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
        if access_token.application is None:
            raise ValueError("#99#: Token không hợp lệ hoặc đã bị xóa.")
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


def encode_json_with_config(json_string: str, config_json: str) -> str:
    """
    Applies a custom, turn-based encoding to a JSON string.

    For each turn, it first inserts prefixes and suffixes at specified indices
    and then applies Base64 encoding to the entire string.

    Args:
        json_string (str): The initial JSON string to be encoded.
        config_json (str): A JSON string containing the encoding configuration.

    Returns:
        str: The final encoded string after all turns are completed.

    Raises:
        ValueError: If the configuration JSON is invalid or missing required keys.
        IndexError: If an insertion index is out of the bounds of the string.
    """
    try:
        config: Dict[str, Any] = json.loads(config_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON configuration string: {e}")

    turns: int = config.get("turns", 0)
    prefix: str = config.get("prefix", "")
    suffix: str = config.get("suffix", "")
    additions: List[Dict[str, Any]] = config.get("additions", [])

    if not isinstance(turns, int) or turns < 0:
        raise ValueError(
            "Configuration 'turns' must be a non-negative integer.")

    encoded_string: str = json_string

    # Loop through each turn
    for current_turn in range(1, turns + 1):
        # 1. Apply string additions for the current turn
        turn_additions = [
            add for add in additions if add.get("turn") == current_turn]

        # Sort additions by index in descending order to prevent index shifts
        # when adding multiple items in the same turn.
        turn_additions.sort(key=lambda x: x.get("index", 0), reverse=True)

        for addition in turn_additions:
            index = addition.get("index")
            add_type = addition.get("type")

            if not isinstance(index, int) or index < 0 or index > len(encoded_string):
                raise IndexError(
                    f"Index {index} is out of bounds for string length {len(encoded_string)} at turn {current_turn}."
                )

            # Insert the prefix or suffix
            if add_type == "prefix":
                encoded_string = (
                    encoded_string[:index] + prefix + encoded_string[index:]
                )
            elif add_type == "suffix":
                encoded_string = (
                    encoded_string[:index] + suffix + encoded_string[index:]
                )

        # 2. After additions, apply Base64 encoding to the entire string.
        # This becomes the input for the next turn.
        encoded_string = base64.b64encode(encoded_string.encode("utf-8")).decode(
            "utf-8"
        )

    return encoded_string


def decode_json_with_config(encoded_string: str, config_json: str) -> str:
    """
    Applies a custom, turn-based decoding to an encoded string.

    For each turn, it first applies Base64 decoding to the entire string
    and then removes prefixes and suffixes that were inserted.

    Args:
        encoded_string (str): The final encoded string to be decoded.
        config_json (str): A JSON string containing the encoding configuration
                           that was used to produce the encoded string.

    Returns:
        str: The original JSON string.

    Raises:
        ValueError: If the configuration JSON is invalid, the string
                    cannot be Base64 decoded, or the prefix/suffix cannot be found.
        IndexError: If an insertion index is out of the bounds of the string.
    """
    try:
        config: Dict[str, Any] = json.loads(config_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON configuration string: {e}")

    turns: int = config.get("turns", 0)
    prefix: str = config.get("prefix", "")
    suffix: str = config.get("suffix", "")
    additions: List[Dict[str, Any]] = config.get("additions", [])

    if not isinstance(turns, int) or turns < 0:
        raise ValueError(
            "Configuration 'turns' must be a non-negative integer.")

    decoded_string: str = encoded_string

    # Loop backwards through each turn, reversing the encoding process
    for current_turn in range(turns, 0, -1):
        # 1. Apply Base64 decoding first, reversing the last encoding step.
        try:
            decoded_string = base64.b64decode(decoded_string.encode("utf-8")).decode(
                "utf-8"
            )
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            raise ValueError(
                f"Base64 decoding failed at turn {current_turn}: {e}")

        # 2. After decoding, remove the string additions for the current turn.
        turn_additions = [
            add for add in additions if add.get("turn") == current_turn]

        # Sort additions by index in ascending order for correct removal.
        turn_additions.sort(key=lambda x: x.get("index", 0), reverse=False)

        for addition in turn_additions:
            index = addition.get("index")
            add_type = addition.get("type")

            if not isinstance(index, int) or index < 0:
                raise IndexError(
                    f"Index {index} is invalid at turn {current_turn}.")

            # Define the marker and its length for removal
            marker = prefix if add_type == "prefix" else suffix
            marker_len = len(marker)

            # Check if the marker is at the expected location before removing it.
            if decoded_string[index: index + marker_len] == marker:
                decoded_string = (
                    decoded_string[:index] +
                    decoded_string[index + marker_len:]
                )
            else:
                raise ValueError(
                    f"Expected '{add_type}' marker '{marker}' not found at index {index} during decode turn {current_turn}."
                )

    return decoded_string


def CHECK_TOKEN_AUTHEN_OF_HEADER_AUTHORIZATION(authorization):
    auth_header = authorization

    if not auth_header:
        raise ValueError("#99#: Yêu cầu đăng nhập.")

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
            logger_bug_string_socket.warning(
                ResponseBase.STATUS_BAD_REQUEST,
                "LỖI CẤU HÌNH THAM SỐ 'KEY_AUTHORIZATION'",
                f"Warning: Configuration for KEY_AUTHORIZATION is not a valid: '{key_prefix_config}'. Using default value.",
            )

    if not auth_header or not auth_header.startswith(f"{key_prefix} "):
        logger_bug_string_socket.warning(
            ResponseBase.STATUS_BAD_REQUEST,
            "CLIENT SEND 'KEY_AUTHORIZATION' SAI!",
            f"Yêu cầu sử dụng KEY: '{key_prefix}'",
        )
        # No Bearer token, let other authentication classes handle or remain anonymous
        return None, None

    token_value = auth_header.split(" ")[1]
    try:
        # Cập nhật
        access_token = AccessToken.objects.select_related("user").get(
            access_token=token_value
        )
        if access_token.application is None:
            raise ValueError("#99#: Token không hợp lệ hoặc đã bị xóa.")
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
        raise AuthenticationFailed(f"#03#: Lỗi hệ thống! {str(e)}")
