from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response, APIView
from ..models import *
from ..serializers import *
from datetime import datetime
from ..throttles import *
import math
from django.conf import settings
from django.shortcuts import render
from ..utils.ResponseMessage import *
from ..logging_ultils import *
from ..queries import Queries
from ..perms import *
from ..utils.CodeGenerate import *
from IT_OAUTH.models import User
from IT_OAUTH.serializers import *
from ..paginations import Paginations
from general_utils.ResponseBase import ResponseBase
import os
import zipfile
from io import BytesIO
from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
import collections

# /(?P<id>[a-zA-Z0-9]+)
# Khoa Khám Bệnh


class DefaultViewSetBase(
    viewsets.ViewSet,
):
    queryset = User.objects.using("oauth").all()
    throttle_classes = [SuperRateThrottle]
    # serializer_class = UserSerializer
    parser_classes = [
        parsers.MultiPartParser,
    ]

    def get_permissions(self):
        if self.action in []:
            return [RoleAppDefault()]

        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    # Màn hình lấy mẫu của các phòng khám
    @action(methods=["get"], detail=False, url_path="get/ds-khoaphong", name="")
    def get_ds_khoaphong(self, request):
        # init response
        response = {}

        # Dieu kien
        where = {
            "sodong": "",
        }

        page_config = {"from": 0, "amount": Paginations.NUM_PAGES_DEFAULT}

        # Set dieu kien
        # sodong = request.query_params.get('sodong')
        # if sodong:
        #    where['sodong'] = sodong

        result = Queries.get_danhsach_khoaphong_nk(where=where, page_config={})
        if result.status == 1:
            response["data"] = result.data
            response["message"] = result.message
            response["result"] = 1
            response["status_code"] = 200
        else:
            response["data"] = result.data
            response["message"] = result.message
            response["result"] = 0
            response["status_code"] = 499

        return Response(response, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------- POST ----------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(detail=False, methods=["get"], url_path="download/files/(?P<folder_name>[^/.]+)", throttle_classes=[HighRateThrottle])
    def download_folder_zip(self, request, folder_name):
        base_path = os.path.join(settings.MEDIA_ROOT, "hoinghi")
        folder_path = os.path.join(base_path, folder_name)

        if not os.path.isdir(folder_path):
            raise Http404("Folder does not exist.")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folder_path)
                    zip_file.write(file_path, arcname=relative_path)

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{smart_str(folder_name)}.zip"'
        return response
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------- PUT ------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
