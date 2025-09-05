from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()

# Template
r.register("xn", views.TemplateViewSet)

r.register("api/default", views.DefaultViewSet)
r.register("api/pub/xn", views.XN_DVYeuCauViewSet)

urlpatterns = [
    path("", include(r.urls)),
    # Add the custom APIView here
]
