from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register(r'api/users', views.UserView)
r.register(r'api/applications', views.ApplicationView)

# Template
r.register(r'', views.DefaultView)

urlpatterns = [
    path('', include(r.urls)),
]
