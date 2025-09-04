# =========================================================================
# File: app/consumers.py
# Description: A base WebSocket consumer that automatically logs all events.
# =========================================================================
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# models
from IT_SOCKET_SYS.models import WebSocketLog, ConfigApp as ConfigAppSocket

# general_utils
from general_utils.utils import *
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.GetConfig.UtilsAuthen import CHECK_TOKEN_AUTHEN_OF_HEADER_AUTHORIZATION
from general_utils.Logging.logging_tools import LogHelper, LogHelperOnlyString

# Logger sys
logger_bug_string_socket = LogHelperOnlyString("log_socket_bug")


@database_sync_to_async
def create_log_entry(connection_id, user, direction, group, payload):
    """
    Creates a new log entry in the WebSocketLog model.
    This function is wrapped to run in a synchronous thread,
    preventing it from blocking the async event loop.
    """
    WebSocketLog.objects.create(
        connection_id=connection_id,
        user=user,
        message_direction=direction,
        group_name=group,
        payload=payload
    )


@database_sync_to_async
def check_and_get_user_async(auth_header):
    """
    An asynchronous wrapper for the synchronous authentication function.
    This allows CHECK_TOKEN_AUTHEN_OF_HEADER_AUTHORIZATION to be
    called safely from an async context without blocking.
    """
    return CHECK_TOKEN_AUTHEN_OF_HEADER_AUTHORIZATION(auth_header)


class BaseConsumer(AsyncWebsocketConsumer):
    """
    A foundational consumer class that handles connection, disconnection,
    and message reception, with built-in logging for all events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize instance variables to None for later assignment
        self.user = None
        self.access_token = None
        self.group_name = None

    async def connect(self):
        """
        Handles a new WebSocket connection.
        Logs the connection event and accepts the connection.
        """
        # Acknowledge the connection
        await self.accept()

        # Get the user and group name from the scope
        # Correctly get the authorization header by searching the list of tuples
        auth_header = None
        for header, value in self.scope.get('headers', []):
            if header == b'authorization':
                auth_header = value.decode('utf-8')
                break

        try:
            # Check the token authentication using the async wrapper
            if auth_header:
                user, access_token = await check_and_get_user_async(auth_header)
                self.user = user
                self.access_token = access_token
        except Exception as e:
            self.user = None
            self.access_token = None
            logger_bug_string_socket.warning(
                ResponseBase.STATUS_BAD_REQUEST,
                "BaseConsumer::connect Error",
                f"Authentication failed: {str(e)}",
            )

        # Log the connection event
        await create_log_entry(
            connection_id=self.channel_name,
            user=self.user if self.user else None,
            direction='received',
            group=self.group_name,
            payload={'message': 'WebSocket connection established.'}
        )

    async def disconnect(self, close_code):
        """
        Handles the WebSocket disconnection event.
        Logs the disconnection before the channel is closed.
        """
        # Log the disconnection event
        await create_log_entry(
            connection_id=self.channel_name,
            user=self.user if self.user else None,
            direction='sent',
            group=self.group_name,
            payload={'message': 'WebSocket connection closed.'}
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the WebSocket.
        This method logs the message payload before any processing.
        """
        # Determine the payload based on the message type
        if text_data:
            payload = json.loads(text_data)
        else:
            payload = {'message': 'Binary data received.'}

        # Log the received message
        await create_log_entry(
            connection_id=self.channel_name,
            user=self.user if self.user else None,
            direction='received',
            group=self.group_name,
            payload=payload
        )

        # You would add your custom message-handling logic here
        # For example, sending a response back to the client or to a group
        # await self.send(text_data=json.dumps({"status": "Message received."}))
