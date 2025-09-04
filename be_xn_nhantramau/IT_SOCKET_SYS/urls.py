from django.urls import path, include
from rest_framework import routers
from . import views
from .routing_ws import websocket_urlpatterns

r = routers.DefaultRouter()
r.register('socket', views.DefaultViewSet)

urlpatterns = [
    path('', include(r.urls)),
] + websocket_urlpatterns
