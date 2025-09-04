"""
ASGI config for be_noibo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

from IT_SOCKET_SYS.routing_ws import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django_asgi_api = get_asgi_application()


application = ProtocolTypeRouter({
    'http': django_asgi_api,
    'websocket': AllowedHostsOriginValidator(URLRouter(websocket_urlpatterns))
})
