from IT_SOCKET_SYS.models import *


# ---------------------------- #
# ---------------------------- #
# ---------- Utils ----------- #
# ---------------------------- #
# ---------------------------- #
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


async def send_async_general_notify(group_name: str, payload: dict):
    """
    Sends a custom notification message to a specific WebSocket group asynchronously.

    This function should be used within an existing asynchronous context,
    such as a Channels Consumer or an async view.

    Args:
        model_name (str): The name of the model from the URL path (e.g., "user", "doctor").
        payload (dict): The dictionary containing the custom data to be sent.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        print("Error: Channel layer is not configured.")
        return

    # Construct the group name based on the URL path pattern
    # This must match the group name used in the consumer's `connect` method.
    group_name = f"GENERAL_NOTIFY_SYS_{group_name}"

    # Prepare the message to send to the group.
    # The "type" field maps to the method in your consumer (e.g., `notify.message` -> `def notify_message`).
    message = {
        'type': 'notify.message',
        'group_name': group_name,
        'payload': payload,
    }

    print(f"Sending async message to group '{group_name}'...")
    await channel_layer.group_send(group_name, message)
    print("Message sent.")


def send_sync_general_notify(group_name: str, payload: dict):
    """
    Sends a custom notification message to a specific WebSocket group from a
    synchronous context.

    This is useful for calling from a traditional Django view, a signal handler,
    or a management command. It automatically wraps the async call.

    Args:
        model_name (str): The name of the model from the URL path.
        payload (dict): The dictionary containing the custom data.
    """
    # Use async_to_sync to call the asynchronous function from a synchronous context.
    # This is necessary because Django's ORM and most views are synchronous.
    try:
        async_to_sync(send_async_general_notify)(
            group_name, payload)
    except Exception as e:
        print(f"Error sending synchronous notification: {e}")
