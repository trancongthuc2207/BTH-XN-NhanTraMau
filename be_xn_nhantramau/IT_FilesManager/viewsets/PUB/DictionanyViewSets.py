# Standard Library
import math
from datetime import datetime, timedelta

# Django Core
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import OuterRef, Subquery
from django.shortcuts import render

# Django REST Framework
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.utils import *

# External/Internal OAuth App
from IT_OAUTH.serializers import *


# /(?P<id>[a-zA-Z0-9]+)
# Khoa Khám Bệnh


class DictionanyViewSetBase(
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
            "put_multi_id_reject_thanhvien_hoinghi_upload",
        ]:
            return [RoleAppDefault()]

        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["get"], detail=False, url_path="get-dm", name="")
    def GET_dictionary_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = build_advanced_filters_and_pagination(
                request, Dictionary)

            queryset = Dictionary.objects.filter(**filters, active=1)

            # Apply ordering
            if pagination["ordering"]:
                queryset = queryset.order_by(pagination["ordering"])

            # Paginate manually
            paginator = Paginator(queryset, pagination["limit"])
            try:
                page_obj = paginator.page(pagination["page"])
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            data = DictionarySerializer(page_obj, many=True).data

            # Response final
            response.set_data({
                "params": params,
                "pagination": pagination,
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": pagination["page"],
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
            response.set_status(ResponseBase.STATUS_OK)
            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    @action(methods=["get"], detail=False, url_path="get-dm-file-infor", name="")
    def GET_dictionary_file_infor_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = build_advanced_filters_and_pagination(
                request, Dictionary)

            queryset = Dictionary.objects.filter(**filters, active=1)

            # Apply ordering
            if pagination["ordering"]:
                queryset = queryset.order_by(pagination["ordering"])

            # Paginate manually
            paginator = Paginator(queryset, pagination["limit"])
            try:
                page_obj = paginator.page(pagination["page"])
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            data = DictionarySerializer(page_obj, many=True).data

            # Response final
            response.set_data({
                "params": params,
                "pagination": pagination,
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": pagination["page"],
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
            response.set_status(ResponseBase.STATUS_OK)
            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
