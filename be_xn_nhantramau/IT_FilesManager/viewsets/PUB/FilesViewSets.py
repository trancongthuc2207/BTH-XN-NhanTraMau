# Standard Library
import math
import zipfile
from io import BytesIO
from datetime import datetime, timedelta


# Django Core
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import OuterRef, Subquery
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import Http404

# Django REST Framework
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

# Internal Apps
from IT_FilesManager.enums.default_enum import *
from IT_FilesManager.models import *
from IT_FilesManager.paginations import Paginations
from IT_FilesManager.perms import *
from IT_FilesManager.queries import Queries
from IT_FilesManager.serializers import *
from IT_OAUTH.throttles import *
from IT_FilesManager.utils.CodeGenerate import *
from IT_FilesManager.utils.ResponseMessage import *
from IT_FilesManager.utils.Utils import *

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.utils import *
from general_utils.Logging.logging_tools import LogHelper

# External/Internal OAuth App
from IT_OAUTH.serializers import *

#
from IT_FilesManager.Serializers import (
    FilesSerializers
)

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")
# /(?P<id>[a-zA-Z0-9]+)
# Khoa Khám Bệnh


class FilesViewSetBase(
    viewsets.ViewSet,
):
    queryset = Files.objects.using("default").all()
    throttle_classes = [SuperRateThrottle]
    # serializer_class = UserSerializer
    parser_classes = [
        parsers.MultiPartParser,
    ]

    def get_permissions(self):
        if self.action in [
            # GET
            "get_thanhvien_upload_all",
            # PUT
            "put_multi_id_accept_thanhvien_hoinghi_upload"
        ]:
            return [RoleAppDefault()]

        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["get"], detail=False, url_path="get-dm", name="")
    def GET_files_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = build_advanced_filters_and_pagination(
                request, Files, exclude_filter=["join_information_file_value"])

            queryset = Files.objects.filter(**filters, active=1)
            # JOINS
            extra_params = {
                'joins': [
                    {
                        "model_join": FileInformation,
                        'conditions': {
                            'key': 'THONG_TIN_CHUNG',
                            'value__icontains': request.query_params.get('join_information_file_value', '')
                        }
                    }
                ]
            }
            queryset = add_extra_conditions_to_queryset(
                queryset, extra_params)

            # Dictionary map
            data_map = DICTIONARY_FILE_INFOR(request)
            #

            # Apply ordering
            if pagination["ordering"]:
                queryset = queryset.order_by(pagination["ordering"])

            # Paginate manually
            paginator = Paginator(queryset, pagination["limit"])
            try:
                page_obj = paginator.page(pagination["page"])
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            data = FilesSerializers.FilesFull_InforSerializer(
                page_obj, many=True).data

            # Response final
            response.set_data({
                "params": params,
                "pagination": pagination,
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": pagination["page"],
                "data_map": data_map,
                "data": data
            })
            response.set_message("Không có dữ liệu nào!" if len(
                data) == 0 else "Lấy dữ liệu thành công!")
            response.set_status(ResponseBase.STATUS_OK)

            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])
        except Exception as e:
            # Response final
            response.set_data({
                "params": None,
                "pagination": None,
                "count": None,
                "total_pages": None,
                "current_page": None,
                "data": None
            })
            response.set_message("Lấy dữ liệu không thành công!")
            response.add_error(
                {
                    "code": 00,
                    "message": str(e)
                }
            )
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "GET_files_all",
                                   f"GET_files_all: {str(e)}")
            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    @action(detail=False, methods=["post"], url_path="download/by-ids")
    def download_files_by_id(self, request):
        """
        Downloads a zip file containing a list of files identified by their IDs.
        The files within the zip are renamed to their 'file_name' property.

        This endpoint expects a POST request with a JSON body containing a list of file IDs.

        Example JSON body:
        {
            "file_ids": [1, 5, 8, 12]
        }
        """
        # 1. Get and validate the list of file IDs from the request body.
        file_ids = json.loads(request.data.get("file_ids", "[]"))
        if not file_ids or not isinstance(file_ids, list):
            raise ValidationError({"error": "A list of file IDs is required."})

        # 2. Query the database for the files.
        # Use a list to store found files and a set for quick ID lookup.
        files_to_zip = []
        found_ids = set()

        # Iterate through the provided IDs to maintain order and handle non-existent files.
        for file_id in file_ids:
            try:
                # Use get_object_or_404 for clean error handling if a single file is not found.
                file_obj = get_object_or_404(Files, pk=file_id)
                files_to_zip.append(file_obj)
                found_ids.add(file_id)
            except Http404:
                # If a file is not found, we can choose to raise an error
                # or log it and continue. Raising an error is generally
                # better for API integrity.
                raise NotFound(f"File with ID {file_id} not found.")

        # 3. Create a zip archive in memory.
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 4. Loop through the retrieved files and add them to the zip.
            for file_obj in files_to_zip:
                # Ensure the physical file exists on the server before trying to add it.
                if not file_obj.file.storage.exists(file_obj.file.name):
                    # You might want to log this or handle it as an error.
                    # For this example, we'll raise an error.
                    raise NotFound(
                        f"Physical file for '{file_obj.file_name}' (ID: {file_obj.pk}) does not exist on the server.")

                # Get the full path of the file on the filesystem.
                file_path = file_obj.file.path

                # Add the file to the zip with a custom name.
                # The 'arcname' parameter renames the file inside the zip archive.
                zip_file.write(
                    file_path, arcname=smart_str(file_obj.file_name))

        # 5. Prepare and return the HTTP response.
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")

        # Set the filename for the downloaded zip file.
        response["Content-Disposition"] = 'attachment; filename="selected_files.zip"'

        return response
