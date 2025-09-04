from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
# PUB
r.register("api/pub/default", views.DefaultViewSet)
r.register("api/pub/default/dictionary", views.DictionanyViewSet)
r.register("api/pub/default/file-category", views.FileCategoryViewSet)
r.register("api/pub/default/file-type", views.FileTypeViewSet)
r.register("api/pub/default/files-manager", views.FilesViewSet)
# PRIV
r.register("api/priv/default/file-category", views.PRIV_FileCategoryViewSet)
r.register("api/priv/default/file-type", views.PRIV_FileTypeViewSet)
r.register("api/priv/default/files-manager", views.PRIV_FilesViewSet)

urlpatterns = [
    path("", include(r.urls))
]
