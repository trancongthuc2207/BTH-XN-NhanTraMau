from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
# PUB
r.register("api/pub/default", views.DefaultViewSet)
r.register("api/pub/mail-manager", views.FormMailViewSet)
# PRIV

urlpatterns = [path("", include(r.urls))]
