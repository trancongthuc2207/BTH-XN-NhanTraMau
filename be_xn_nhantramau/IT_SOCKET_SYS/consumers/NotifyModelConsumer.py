# =========================================================================
# File: app/consumers.py
# Description: Fixed asynchronous consumer, removed unnecessary async_to_sync wrappers.
# =========================================================================
import json
# Removed unused imports: async_to_sync and database_sync_to_async
from IT_SOCKET_SYS.consumers.BaseConsumer import BaseConsumer, create_log_entry
# from datetime import datetime

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.utils import *
from general_utils.Logging.logging_tools import LogHelper, LogHelperOnlyString

# Logger sys
logger_info_string_sys = LogHelperOnlyString("file_info_sys")
logger_bug_string_sys = LogHelperOnlyString("file_bug_sys")


class NotifyModelConsumerBase(BaseConsumer):
    """
    An asynchronous WebSocket consumer that handles real-time notifications
    for specific models. It extends BaseConsumer to inherit logging.
    """
    URL_PATH = r"ws/notify/(?P<model_name>[\w\d]+)/change/(?P<id>\w+)"

    async def connect(self):
        """
        Handles a new connection and joins the correct notification group.
        This method calls the parent connect() to ensure logging.
        """
        # Retrieve the URL parameters to form the unique group name
        self.model_name = self.scope["url_route"]["kwargs"]["model_name"]
        self.item_id = self.scope["url_route"]["kwargs"]["id"]
        self.group_name = f"notify_{self.model_name}_{self.item_id}"

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Call the parent connect() to handle logging and accepting the connection
        await super().connect()

    async def disconnect(self, close_code):
        """
        Leaves the group and then calls the parent disconnect() to handle logging.
        """
        # Leave the group on disconnect
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        # Call the parent disconnect() to handle logging
        await super().disconnect(close_code)

    async def notify_message(self, event):
        """
        Receives a message from the group and sends it to the client.
        The method name matches the 'type' key in the message payload.
        """
        payload = event['payload']
        # You can add logging here for messages sent to the client
        await create_log_entry(
            connection_id=self.channel_name,
            user=self.user if self.user else None,
            direction='sent',
            group=self.group_name,
            payload=payload
        )
        await self.send(text_data=json.dumps(payload))
