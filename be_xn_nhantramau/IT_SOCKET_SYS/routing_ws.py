from .consumer import *
from django.urls import re_path

websocket_urlpatterns = [
    # WebSocket route for specific chat rooms
    re_path(ChatConsumer.URL_PATH, ChatConsumer.as_asgi()),
    re_path(NotifyConsumer.URL_PATH, NotifyConsumer.as_asgi()),
]
