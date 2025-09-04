# ---------------------------- #
# ---------------------------- #
# ---------- Utils ----------- #
# ---------------------------- #
# ---------------------------- #
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Models
from IT_SOCKET_SYS.models import ConfigApp
from general_utils.Logging.logging_tools import LogHelper, LogHelperOnlyString
from general_utils.utils import split_and_clean

# Logger sys
logger_info_string_sys = LogHelperOnlyString("file_info_sys")
logger_bug_string_sys = LogHelperOnlyString("file_bug_sys")
logger_bug_string_sys_socket = LogHelperOnlyString("log_socket_bug")


def GET_LIST_MODELS_EXCLUDE_NOTIFY_CHANGE(action_name, dbname="default"):
    data = []
    try:
        config_action = (
            ConfigApp.objects.using(dbname)
            .filter(name_config=action_name, status=True, is_used=True, active=True)
            .first()
        )
        if not config_action:
            return data

        data = split_and_clean(config_action.value, ",")
    except Exception as e:
        logger_bug_string_sys.warning(
            400,
            "LỖI CẤU HÌNH THAM SỐ 'LIST_MODELS_EXCLUDE_NOTIFY_CHANGE'",
            f"Warning: Configuration for '{action_name}'. {str(e)}",
        )
        return []
    return data


async def send_async_model_notification(model_name: str, item_id: str, payload: dict):
    """
    Sends a custom notification message to a specific WebSocket group asynchronously.

    This function should be used within an existing asynchronous context,
    such as a Channels Consumer or an async view.

    Args:
        model_name (str): The name of the model from the URL path (e.g., "user", "doctor").
        item_id (str): The ID of the specific item to notify (e.g., a user's ID).
        payload (dict): The dictionary containing the custom data to be sent.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        print("Error: Channel layer is not configured.")
        return

    # Construct the group name based on the URL path pattern
    # This must match the group name used in the consumer's `connect` method.
    group_name = f"notify_{model_name}_{item_id}"

    # Prepare the message to send to the group.
    # The "type" field maps to the method in your consumer (e.g., `notify.message` -> `def notify_message`).
    message = {
        'type': 'notify.message',
        'payload': payload,
    }

    print(f"Sending async message to group '{group_name}'...")
    await channel_layer.group_send(group_name, message)
    print("Message sent.")


def send_sync_model_notification(model_name: str, item_id: str, payload: dict):
    """
    Sends a custom notification message to a specific WebSocket group from a
    synchronous context.

    This is useful for calling from a traditional Django view, a signal handler,
    or a management command. It automatically wraps the async call.

    Args:
        model_name (str): The name of the model from the URL path.
        item_id (str): The ID of the specific item to notify.
        payload (dict): The dictionary containing the custom data.
    """
    # Use async_to_sync to call the asynchronous function from a synchronous context.
    # This is necessary because Django's ORM and most views are synchronous.
    try:
        list_ex = GET_LIST_MODELS_EXCLUDE_NOTIFY_CHANGE(
            "LIST_MODELS_EXCLUDE_NOTIFY_CHANGE")

        if model_name in list_ex:
            logger_info_string_sys.info(
                400,
                "send_sync_model_notification::Info",
                f"{model_name} đang trong danh sách loại trừ thông báo!",
            )
            return

        async_to_sync(send_async_model_notification)(
            model_name, item_id, payload)
    except Exception as e:
        logger_bug_string_sys_socket.warning(
            400,
            "send_sync_model_notification::Error",
            f"Error sending synchronous notification: {e}",
        )
