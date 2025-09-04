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
from IT_FilesManager.models import Files, FileInformation
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
from IT_OAUTH.models import User
from IT_OAUTH.serializers import *
#
from IT_FilesManager.Serializers import (
    FilesSerializers
)

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")

# /(?P<id>[a-zA-Z0-9]+)


class PRIV_FilesViewSetBase(
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
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["get"], detail=False, url_path="get-dm", name="")
    def PRIV_GET_files_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = build_advanced_filters_and_pagination(
                request, Files)

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
            logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "PRIV_GET_files_all",
                                   f"PRIV_GET_files_all: {str(e)}")
            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["post"], detail=False, url_path="multi-create", name="")
    def PRIV_POST_create_multi_files(self, request):
        # init response
        response = ResponseBase()
        try:
            data_body = request.data
            data_add_success = []
            data_add_fail = []
            data_add_detail_fail = []
            # Dictionary map
            data_map = DICTIONARY_FILE_INFOR(request)
            #
            # Template JSON
            # [{"files_infor":"{"FILE_TIEU_DE": "", "FILE_TOM_TAT": "", "FILE_SO_KY_HIEU": "", "FILE_SO_BAN_HANH": "", "FILE_NGAY_BAN_HANH": "", "FILE_NGAY_HIEU_LUC": "", "FILE_NGAY_HET_HIEU_LUC": "", "FILE_NGAY_TAO": "", "FILE_SO_LUONG_XEM": "", "FILE_SO_LUONG_TAI_XUONG": "", "FILE_NGON_NGU": "", "FILE_TAG": "", "FILE_LIEN_QUAN": "", "FILE_ID_NGUOI_DUYET": "", "FILE_TEN_NGUOI_DUYET": "", "FILE_ID_NGUOI_TAO": "", "FILE_TEN_NGUOI_TAO": "", "FILE_ID_NGUOI_CAP_NHAT": "", "FILE_TEN_NGUOI_CAP_NHAT": "", "FILE_ID_NGUOI_DUYET_CAP_NHAT": "", "FILE_TEN_NGUOI_DUYET_CAP_NHAT": "", "FILE_ID_NGUOI_DUYET_CHINH": "", "FILE_TEN_NGUOI_DUYET_CHINH": "", "FILE_TAC_GIA": ""}","description":"abc","category":"","password":"","allowed_view":"1","allowed_download":"1","allơwed_edit":"1","required_authen":"0","is_error":"1","status":"0"}]
            json_string = data_body["list_json"]
            list_json = json.loads(json_string)
            try:
                with transaction.atomic(using="default"):
                    for json_instance in list_json:
                        files = Files()

                        # temp infor
                        infor_temp = json_instance["files_infor"]

                        # asign value
                        files = assign_fields_to_instance(
                            instance=files, data=json_instance, exclude_fields=["files_infor", "file", "fileinformation"], response=response)
                        if files.password:
                            files.password = create_password_hash(
                                files.password)
                        # save
                        files.save()
                        if files.pk:
                            try:
                                files_infor = FileInformation()
                                files_infor.file = files
                                files_infor.key = "THONG_TIN_CHUNG"
                                files_infor.value = infor_temp
                                files_infor.save()
                            except Exception as e:
                                # Logging
                                logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILEs: LỖI THÊM THÔNG TIN",
                                                       f"{str(e)}")

                        data_add_success.append(files)

                    # return response
                    data_response = {
                        "data_add_success": FilesSerializers.FilesFull_InforSerializer(data_add_success, many=True).data,
                        "data_add_fail": FilesSerializers.FilesFull_InforSerializer(data_add_fail, many=True).data,
                        "data_add_detail_fail": data_add_detail_fail,
                        "data_map": data_map
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
            response.add_error({
                "server": str(e)
            })

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    @action(methods=["post"], detail=False, url_path="multi-create-by-code-index", name="")
    def PRIV_POST_create_multi_files_by_code_index(self, request):
        # init response
        response = ResponseBase()
        try:
            data_body = request.data
            data_add_success = []
            data_add_fail = []
            data_add_detail_fail = []
            # Dictionary map
            data_map = DICTIONARY_FILE_INFOR(request)
            #
            # Template JSON
            # [{"code_index":"abc","description":"abc","category":"","password":"","allowed_view":"1","allowed_download":"1","allơwed_edit":"1","required_authen":"0","is_error":"1","status":"0"}]
            json_string = data_body["list_json"]
            list_json = json.loads(json_string)
            try:
                with transaction.atomic(using="default"):
                    for json_instance in list_json:
                        files = Files()
                        # check required
                        if not json_instance["code_index"]:
                            response.set_data(None)
                            response.set_message(
                                "Yêu cầu nhập code phiên bản!")
                            response.set_status(
                                ResponseBase.STATUS_BAD_REQUEST)
                            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

                        # tìm file gần nhất
                        file_master = Files.objects.using("default").filter(
                            code_index=json_instance["code_index"], active=True
                        ).order_by("-sort_index").first()
                        if not file_master:
                            response.set_data(None)
                            response.set_message(
                                "Không tìm thấy bản file nào!")
                            response.set_status(
                                ResponseBase.STATUS_BAD_REQUEST)

                        # asign value
                        files = assign_fields_to_instance(
                            instance=files, data=json_instance, exclude_fields=["file", "fileinformation", "sort_index"], response=response)
                        if files.password:
                            files.password = create_password_hash(
                                files.password)

                        if file_master.sort_index:
                            files.sort_index += file_master.sort_index

                        # save
                        files.save()
                        data_add_success.append(files)

                        # copy infor of master
                        list_files_infor_master = FileInformation.objects.using(
                            "default").filter(file=file_master, active=True)
                        for files_infor_master in list_files_infor_master:
                            files_infor_clone = files_infor_master
                            files_infor_clone.file = files
                            files_infor_clone.pk = None
                            files_infor_clone.save()

                    # return response
                    data_response = {
                        "data_add_success": FilesSerializers.FilesFull_InforSerializer(data_add_success, many=True).data,
                        "data_add_fail": FilesSerializers.FilesFull_InforSerializer(data_add_fail, many=True).data,
                        "data_add_detail_fail": data_add_detail_fail,
                        "data_map": data_map
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
            response.add_error({
                "server": str(e)
            })

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ PUT ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    @action(methods=["put"], detail=False, url_path="update", name="")
    def PRIV_PUT_update_files(self, request):
        # init response
        response = ResponseBase()
        try:
            files = Files()
            data_body = request.data

            try:
                with transaction.atomic(using="default"):
                    # find by id
                    files = Files.objects.using("default").filter(
                        id=data_body["id"], active=True
                    ).first()
                    # Nếu tìm k thấy instance
                    if not files:
                        response.set_data(None)
                        response.set_message(
                            "Không tìm thấy mã nguồn dữ liệu!")
                        response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

                    # asign value
                    files = assign_fields_to_instance(
                        instance=files, data=data_body, exclude_fields=["file"], response=response)
                    if files.password:
                        files.password = create_password_hash(files.password)
                    # save
                    files = write_log(
                        instance=files, request=request)
                    files.save()

                    # return response
                    response.set_data(
                        FilesSerializers.FilesFull_InforSerializer(files).data)
                    response.set_message("Cập nhật nguồn file thành công!")
                    response.set_status(ResponseBase.STATUS_OK)
            except Exception as e:
                # Exception Set Data
                response.set_data(None)
                response.set_message("Lỗi cập nhật thất bại do lỗi hệ thống")
                response.add_error({
                    "server": str(e)
                })
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                # Logging
                logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILEs: LỖI CẬP NHẬT FILEs",
                                       f"{str(e)}")
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Cập nhật nguồn file không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            # Logging
            logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILEs: LỖI CẬP NHẬT FILEs",
                                   f"{str(e)}")

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    @action(methods=["put"], detail=False, url_path="update-after-create", name="")
    def PRIV_PUT_update_files_after_create(self, request):
        # init response
        response = ResponseBase()
        try:
            files = Files()
            data_body = request.data

            try:
                with transaction.atomic(using="default"):
                    # find by id
                    files = Files.objects.using("default").filter(
                        id=data_body["id"], active=True
                    ).first()
                    # Nếu tìm k thấy instance
                    if not files:
                        response.set_data(None)
                        response.set_message(
                            "Không tìm thấy mã nguồn dữ liệu!")
                        response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

                    # asign value
                    files = assign_fields_to_instance(
                        instance=files, data=data_body, exclude_fields=None, response=response)
                    if files.file:
                        files.file_name = files.file.name
                    # save
                    files.save()
                    if files.is_error:
                        files.is_error = False
                        files.save()

                    # return response
                    response.set_data(
                        FilesSerializers.FilesFull_InforSerializer(files).data)
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
                logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILEs: LỖI CẬP NHẬT FILEs",
                                       f"{str(e)}")
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Cập nhật nguồn file không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            # Logging
            logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "FILEs: LỖI CẬP NHẬT FILEs",
                                   f"{str(e)}")
            response.add_error({
                "server": str(e)
            })

        return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])
