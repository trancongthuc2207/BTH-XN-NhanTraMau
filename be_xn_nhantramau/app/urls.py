"""
URL configuration for ChatProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import mimetypes
from django.views.static import serve
from django.http import FileResponse, Http404
import os
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="CHAT APIs",
        default_version="v1",
        description="APIs for CHAT",
        contact=openapi.Contact(email="thuctran.2207@gmail.com"),
        license=openapi.License(name="Trần Công Thức@2024"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Override view file on media file
def serve_media_inline(request, path):
    """
    Phục vụ các file media với Content-Disposition: inline.

    Args:
        request: Đối tượng HttpRequest.
        path (str): Đường dẫn tương đối của file trong MEDIA_ROOT.
    """
    # Lấy đường dẫn tuyệt đối của file
    full_path = os.path.join(settings.MEDIA_ROOT, path)

    # Đảm bảo file tồn tại và nằm trong thư mục MEDIA_ROOT để đảm bảo bảo mật
    if not os.path.exists(full_path):
        raise Http404("File does not exist.")

    if not os.path.normpath(full_path).startswith(os.path.normpath(settings.MEDIA_ROOT)):
        raise Http404("Invalid file path.")

    # Xác định kiểu nội dung (content type) của file
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    # Mở và phục vụ file
    response = FileResponse(open(full_path, 'rb'), content_type=mime_type)

    # Cài đặt header Content-Disposition thành 'inline'
    # Điều này sẽ khiến trình duyệt hiển thị file thay vì tải xuống
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(full_path)}"'

    return response

urlpatterns = [
    path("", include("IT_OAUTH.urls")),
    path("", include("IT_Default.urls")),
    path("", include("IT_FilesManager.urls")),
    path("", include("IT_MailManager.urls")),
    # SOCKET
    path("", include("IT_SOCKET_SYS.urls")),
    #
    path("admin/", admin.site.urls),
    re_path(r"^ckeditor/", include("ckeditor_uploader.urls")),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$',
                serve_media_inline, name='media_inline'),
    ]



