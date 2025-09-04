# =========================================================================
# File: app/consumers.py
# Description: Fixed asynchronous consumer, removed unnecessary async_to_sync wrappers.
# =========================================================================
import json
# Removed unused imports: async_to_sync and database_sync_to_async
from IT_SOCKET_SYS.consumers.BaseConsumer import BaseConsumer
# from datetime import datetime

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.utils import *
from general_utils.Logging.logging_tools import LogHelper, LogHelperOnlyString


# Logger sys
logger_info_string_sys = LogHelperOnlyString("file_info_sys")
logger_bug_string_sys = LogHelperOnlyString("file_bug_sys")


class ChatConsumerBase(BaseConsumer):
    """
    An asynchronous WebSocket consumer that handles real-time chat messages.
    """
    URL_PATH = r"ws/chat/(?P<code_room>[\w\d]+)/(?P<id>\w+)"

    async def connect(self):
        """
        Handles the WebSocket connection event.
        Retrieves room and user IDs from the URL route.
        """
        self.code_room = self.scope["url_route"]["kwargs"]["code_room"]
        self.user_id = self.scope['url_route']['kwargs']['id']
        print(self.code_room)

        self.room_group_name = f"chat_{self.code_room}_1"

        # Corrected: Use await directly on the async function
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()
        print(f"User {self.user_id} connected to room {self.code_room}")

    async def disconnect(self, close_code):
        """
        Handles the WebSocket disconnection event.
        Removes the user from the room group.
        """
        # Corrected: Use await directly on the async function
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        print(f"User {self.user_id} disconnected with code: {close_code}")

    async def receive(self, text_data):
        """
        Receives messages from the WebSocket and sends them to the room group.
        """
        print(text_data)

        try:
            text_data_json = json.loads(text_data)
            print(text_data_json)

            # Corrected: Use await directly on the async function
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat.message",
                    'client': text_data_json
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")
            text_data_json = json.loads(text_data)
            text_data_json['status'] = 0
            text_data_json['notify'] = 'Không thành công, lỗi tìm kiếm!'

            # Corrected: Use await directly on the async function
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat.message",
                    'client': text_data_json
                }
            )
            # Log the error
            logger_bug_string_sys.warning(
                ResponseBase.STATUS_ERROR_DEFAULT,
                f"""ChatConsumerBase:: Error in receive: {e}, text_data: {json.dumps(
                    text_data_json, ensure_ascii=False
                )}"""
            )

    async def chat_message(self, event):
        """
        Receives a message from the room group and sends it to the WebSocket.
        """
        print(f"chat_message :: {event}")

        # Corrected: Use await directly on the async function
        await self.send(text_data=json.dumps(
            {'client': event['client']}, ensure_ascii=False))
