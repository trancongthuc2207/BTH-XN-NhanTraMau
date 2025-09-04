# Standard Library
import math
from datetime import datetime, timedelta

# Django Core
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import OuterRef, Subquery
from django.shortcuts import render
from django.db import connections, transaction  # Import transaction

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


# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelper
from general_utils.utils import *

# External/Internal OAuth App
from IT_OAUTH.serializers import *
#
from IT_FilesManager.Serializers import (
    FileTypeSerializers
)

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")

# /(?P<id>[a-zA-Z0-9]+)


class PRIV_FileTypeViewSetBase(
    viewsets.ViewSet,
):
    queryset = FileType.objects.using("default").all()
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
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["get"], detail=False, url_path="get-dm", name="")
    def PRIV_GET_file_type_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = build_advanced_filters_and_pagination(
                request, FileType)

            queryset = FileType.objects.filter(**filters, active=1)

            # Apply ordering
            if pagination["ordering"]:
                queryset = queryset.order_by(pagination["ordering"])

            # Paginate manually
            paginator = Paginator(queryset, pagination["limit"])
            try:
                page_obj = paginator.page(pagination["page"])
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            data = FileTypeSerializers.FileTypeSerializer(
                page_obj, many=True).data

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
    @action(methods=["post"], detail=False, url_path="create", name="")
    def PRIV_POST_create_file_type(self, request):
        # init response
        response = ResponseBase()
        try:
            file_type = FileType()
            data_body = request.data

            try:
                with transaction.atomic(using="default"):
                    # asign value
                    file_type = assign_fields_to_instance(
                        instance=file_type, data=data_body, exclude_fields=None, response=response)

                    # check exist
                    find_check = FileType.check_existed_name_instance(
                        file_type)
                    if len(find_check) > 0:
                        # Exception Set Data
                        existed_list = FileTypeSerializers.FileTypeSerializer(
                            find_check, many=True).data
                        response.set_data({
                            "existed_list": existed_list
                        })
                        response.set_message(
                            "Đã phát sinh nguồn dữ liệu này!")
                        response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

                    # save
                    file_type.save()

                    # return response
                    response.set_data(
                        FileTypeSerializers.FileTypeSerializer(file_type).data)
                    response.set_message("Tạo nguồn file thành công!")
                    response.set_status(ResponseBase.STATUS_CREATED)
            except Exception as e:
                # Exception Set Data
                response.set_data(None)
                response.set_message("Đăng nhập thất bại do lỗi hệ thống")
                response.add_error({
                    "server": str(e)
                })
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Tạo nguồn file không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    @action(methods=["post"], detail=False, url_path="multi-create", name="")
    def PRIV_POST_create_multi_file_type(self, request):
        # init response
        response = ResponseBase()
        try:
            data_body = request.data
            data_add_success = []
            data_add_fail = []
            data_add_detail_fail = []
            # Template JSON
            # [{"name":"PNG","extension":"png","mimetype":"","description":"Image files"}]
            json_string = data_body["list_json"]
            list_json = json.loads(json_string)
            try:
                with transaction.atomic(using="default"):
                    for json_instance in list_json:
                        file_type = FileType()

                        # asign value
                        file_type = assign_fields_to_instance(
                            instance=file_type, data=json_instance, exclude_fields=None, response=response)

                        # check exist
                        find_check = FileType.check_existed_code_or_key_category_instance(
                            file_type)
                        if len(find_check) > 0:
                            existed_pks = [str(obj.pk) for obj in find_check]
                            data_add_fail.append(file_type)
                            data_add_detail_fail.append(
                                f"'{file_type.code}' hoặc '{file_type.key_category}' đang bị trùng! Danh sách ID trùng [{','.join(existed_pks)}]")
                            continue

                        # save
                        file_type.save()
                        data_add_success.append(file_type)

                    # return response
                    data_response = {
                        "data_add_success": FileTypeSerializers.FileTypeSerializer(data_add_success, many=True).data,
                        "data_add_fail": FileTypeSerializers.FileTypeSerializer(data_add_fail, many=True).data,
                        "data_add_detail_fail": data_add_detail_fail,
                    }
                    response.set_data(data_response)
                    response.set_message("Tạo nhiều nguồn file thành công!")
                    response.set_status(ResponseBase.STATUS_CREATED)
            except Exception as e:
                # Exception Set Data
                response.set_data(None)
                response.set_message("Đăng nhập thất bại do lỗi hệ thống")
                response.add_error({
                    "server": str(e)
                })
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Tạo nguồn file không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ PUT ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    @action(methods=["put"], detail=False, url_path="update", name="")
    def PRIV_PUT_update_file_type(self, request):
        # init response
        response = ResponseBase()
        try:
            file_type = FileType()
            data_body = request.data

            try:
                with transaction.atomic(using="default"):
                    # find by id
                    file_type = FileType.objects.using("default").filter(
                        id=data_body["id"], active=True
                    ).first()
                    # Nếu tìm k thấy instance
                    if not file_type:
                        response.set_data(None)
                        response.set_message(
                            "Không tìm thấy mã nguồn dữ liệu!")
                        response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

                    # asign value
                    file_type = assign_fields_to_instance(
                        instance=file_type, data=data_body, exclude_fields=None, response=response)

                    # check exist
                    find_check = FileType.check_existed_name_instance(
                        file_type)
                    if len(find_check) > 0:
                        # Exception Set Data
                        existed_list = FileTypeSerializers.FileTypeSerializer(
                            find_check, many=True).data
                        response.set_data({
                            "existed_list": existed_list
                        })
                        response.set_message(
                            "Đã phát sinh nguồn dữ liệu này!")
                        response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

                    # save
                    file_type = write_log(
                        instance=file_type, request=request)
                    file_type.save()

                    # return response
                    response.set_data(
                        FileTypeSerializers.FileTypeSerializer(file_type).data)
                    response.set_message("Cập nhật nguồn file thành công!")
                    response.set_status(ResponseBase.STATUS_OK)
            except Exception as e:
                # Exception Set Data
                response.set_data(None)
                response.set_message("Đăng nhập thất bại do lỗi hệ thống")
                response.add_error({
                    "server": str(e)
                })
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                # Logging
                logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILE_type: LỖI CẬP NHẬT FILE_type",
                                       f"{str(e)}")
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Cập nhật nguồn file không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            # Logging
            logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILE_type: LỖI CẬP NHẬT FILE_type",
                                   f"{str(e)}")

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])
