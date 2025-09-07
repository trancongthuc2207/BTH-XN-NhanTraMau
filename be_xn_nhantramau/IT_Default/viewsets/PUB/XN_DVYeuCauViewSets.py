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
from django.db import connections, transaction  # Import transaction

# Django REST Framework
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

# Internal Apps
# from IT_OAUTH.models import *
from IT_FilesManager.enums.default_enum import *
from IT_Default.models import ConfigApp as ConfigAppDefault
from IT_FilesManager.paginations import Paginations
from IT_FilesManager.perms import *
from IT_FilesManager.queries import Queries
from IT_Default.serializers import *
from IT_OAUTH.throttles import *
from IT_FilesManager.utils.Utils import *

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.utils import *
from general_utils.Logging.logging_tools import LogHelper
from general_utils.GetConfig.UtilsConfigSystem import *

from IT_Default.utils.sql_server.sql_utils import (
    sql_build_advanced_filters_and_pagination,
)

# External/Internal OAuth App
from IT_OAUTH.serializers import *

# Serializers
from IT_FilesManager.Serializers import FilesSerializers

# SQL Import
from IT_Default.queries.QueriesFPT_XN_LAYMAU_NHANMAU import *

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")
# /(?P<id>[a-zA-Z0-9]+)
# Khoa Khám Bệnh


class XN_DVYeuCauSetBase(
    viewsets.ViewSet,
):
    queryset = User.objects.using("oauth").all()
    throttle_classes = [SuperRateThrottle]
    # serializer_class = UserSerializer
    parser_classes = [
        parsers.MultiPartParser,
        parsers.JSONParser,  # for application/json
    ]

    def get_permissions(self):
        if self.action in [
            # GET
            "get_thanhvien_upload_all",
            # PUT
            "put_multi_id_accept_thanhvien_hoinghi_upload",
        ]:
            return [RoleAppDefault()]

        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["get"], detail=False, url_path="nhan-mau/all", name="")
    def GET_danhsach_dichvu_yeucau_xn_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = sql_build_advanced_filters_and_pagination(
                request, exclude_filter=["join_information_file_value"]
            )

            print(filters)
            print(pagination)
            print(params)

            str_sql = GET_VALUE_ACTION_SYSTEM(
                ConfigAppDefault, "SQL_DS_DVYC_ALL", "default"
            )
            # print(str_sql)
            # varriables = extract_template_variables(str_sql)
            is_render, str_sql_render = render_template_string(str_sql, params)
            # print(str_sql_render)

            result, infor_more = EXCUTE_SQL(
                str_sql=str_sql_render,
                sort=pagination["ordering"],
                page_config={
                    "from": (pagination["page"] - 1) * pagination["limit"],
                    "amount": pagination["limit"],
                },
            )
            # print(result)
            for xn in result.data:
                filters_ghinhan = GhiNhanMauXetNghiem.objects.using("default").filter(
                    active=1, DVYEUCAU_ID=str(xn["DVYEUCAU_ID"])
                )
                xn["LIST_GHINHAN"] = GhiNhanMauXetNghiemLessDataSerializer(
                    filters_ghinhan, many=True
                ).data

            # Response final
            response.set_data(
                {
                    "params": params,
                    "pagination": pagination,
                    # "count": paginator.count,
                    # "total_pages": paginator.num_pages,
                    "current_page": pagination["page"],
                    "infor_more": infor_more,
                    "data": result.data,
                }
            )
            response.set_message(result.message)
            response.set_status(ResponseBase.STATUS_OK)

            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
        except Exception as e:
            # Response final
            response.set_data(
                {
                    "params": None,
                    "pagination": None,
                    "count": None,
                    "total_pages": None,
                    "current_page": None,
                    "infor_more": None,
                    "data": None,
                }
            )
            response.set_message("Lấy dữ liệu không thành công!")
            response.add_error({"code": 00, "message": str(e)})
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            logger_bug_sys.warning(
                request,
                ResponseBase.STATUS_BAD_REQUEST,
                "GET_danhsach_dichvu_yeucau_xn_all",
                f"GET_danhsach_dichvu_yeucau_xn_all: {str(e)}",
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    @action(methods=["get"], detail=False, url_path="nhan-mau/check-laymau", name="")
    def GET_check_edit_laymau(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = sql_build_advanced_filters_and_pagination(
                request, exclude_filter=["join_information_file_value"]
            )

            print(filters)
            print(pagination)
            print(params)

            str_sql = GET_VALUE_ACTION_SYSTEM(
                ConfigAppDefault, "SQL_CHECK_EDIT_DVYEUCAU", "default"
            )
            # print(str_sql)
            # varriables = extract_template_variables(str_sql)
            is_render, str_sql_render = render_template_string(str_sql, params)
            # print(str_sql_render)

            result, infor_more = EXCUTE_SQL(
                str_sql=str_sql_render, sort=None, page_config=None
            )

            # Response final
            response.set_data({"params": params, "data": result.data})
            response.set_message(result.message)
            response.set_status(ResponseBase.STATUS_OK)

            if result.status == 0:
                response.set_status(ResponseBase.STATUS_BAD_GATEWAY)

            # Kiểm tra đã lấy mẫu - (trường hợp đã nhận mẫu và bên his nhảy trạng thai chưa thực hiện)
            details_ghinhan = []
            type_last = ""
            if result.data:
                if result.data[0]:
                    # Lấy dữ liệu show
                    if result.data[0]["EDIT_CHECK"] in ["TRUE", "FALSE"]:
                        list_ghinhan = (
                            GhiNhanMauXetNghiem.objects.using("default")
                            .filter(**params, active=True)
                            .order_by("-created_date", "sort_index")
                        )
                        # lấy type cuối cùng
                        for gn in list_ghinhan:
                            type_last = gn.type
                            break
                        details_ghinhan = GhiNhanMauXetNghiemLessDataSerializer(
                            list_ghinhan, many=True
                        ).data
                    result.data[0]["type_last"] = type_last
                    result.data[0]["details_ghinhan"] = details_ghinhan
                    if details_ghinhan and result.data[0]["EDIT_CHECK"] == "TRUE":
                        # re-SET dữ liệu
                        result.data[0]["EDIT_CHECK"] = "FALSE"
                        result.data[0][
                            "MESSAGE_CHECK"
                        ] = "Đã có ghi nhận lấy mẫu! Vui lòng kiểm tra lại."

                        # set lại response
                        response.set_data({"params": params, "data": result.data})
                        response.set_message(
                            "Đã có ghi nhận lấy mẫu! Vui lòng kiểm tra lại."
                        )
                        # response.set_status(ResponseBase.STATUS_BAD_GATEWAY)

            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
        except Exception as e:
            # Response final
            response.set_data({"params": None, "data": None})
            response.set_message("Lấy dữ liệu không thành công!")
            response.add_error({"code": 00, "message": str(e)})
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            logger_bug_sys.warning(
                request,
                ResponseBase.STATUS_BAD_REQUEST,
                "GET_check_edit_laymau",
                f"GET_check_edit_laymau: {str(e)}",
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    @action(methods=["get"], detail=False, url_path="nhan-mau/check-nhanmau", name="")
    def GET_check_edit_nhanmau(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = sql_build_advanced_filters_and_pagination(
                request, exclude_filter=["join_information_file_value"]
            )

            print(filters)
            print(pagination)
            print(params)

            str_sql = GET_VALUE_ACTION_SYSTEM(
                ConfigAppDefault, "SQL_CHECK_EDIT_NHANMAU_DVYEUCAU", "default"
            )
            # print(str_sql)
            # varriables = extract_template_variables(str_sql)
            is_render, str_sql_render = render_template_string(str_sql, params)
            # print(str_sql_render)

            result, infor_more = EXCUTE_SQL(
                str_sql=str_sql_render, sort=None, page_config=None
            )

            # Response final
            response.set_data({"params": params, "data": result.data})
            response.set_message(result.message)
            response.set_status(ResponseBase.STATUS_OK)

            if result.status == 0:
                response.set_status(ResponseBase.STATUS_BAD_GATEWAY)

            # Kiểm tra đã lấy mẫu - trước khi nhận mẫu
            details_ghinhan = []
            type_last = ""
            if result.data:
                if result.data[0]:
                    # Lấy dữ liệu show
                    if result.data[0]["EDIT_CHECK"] in ["TRUE", "FALSE"]:
                        list_ghinhan = (
                            GhiNhanMauXetNghiem.objects.using("default")
                            .filter(**params, active=True)
                            .order_by("-created_date", "sort_index")
                        )
                        # lấy type cuối cùng
                        for gn in list_ghinhan:
                            type_last = gn.type
                            break
                        details_ghinhan = GhiNhanMauXetNghiemLessDataSerializer(
                            list_ghinhan, many=True
                        ).data
                    result.data[0]["type_last"] = type_last
                    result.data[0]["details_ghinhan"] = details_ghinhan

                    # yêu cầu phải có ghi nhận + EDIT_CHECK = TRUE
                    if not details_ghinhan and result.data[0]["EDIT_CHECK"] == "TRUE":
                        result.data[0]["EDIT_CHECK"] = "FALSE"
                        result.data[0][
                            "MESSAGE_CHECK"
                        ] = "Chưa có ghi nhận lấy mẫu nào!"
                        response.set_data({"params": params, "data": result.data})
                        response.set_message("Chưa có ghi nhận lấy mẫu nào!")

                    # Có ghi nhận và kiểm tra những ghi nhận + EDIT_CHECK = TRUE
                    if details_ghinhan and result.data[0]["EDIT_CHECK"] == "TRUE":
                        str_check = "TRUE"
                        mess_check = result.data[0]["MESSAGE_CHECK"]

                        # kiểm tra lần ghi nhận cuối có phải là KHOA LS lấy mẫu k
                        if type_last not in ["KHOALS_LAYMAU"]:
                            str_check = "FALSE"
                            mess_check = "Hiện tại khoa Lâm Sàng chưa lấy mẫu!"

                        if type_last in ["KHOAXN_NHANMAU"]:
                            str_check = "FALSE"
                            mess_check = "Hiện tại đã có ghi nhận lần nhận mẫu!"

                        # re-SET dữ liệu
                        result.data[0]["EDIT_CHECK"] = str_check
                        result.data[0]["MESSAGE_CHECK"] = mess_check

                        # set lại response
                        response.set_data({"params": params, "data": result.data})
                        response.set_message(mess_check)
                        # response.set_status(ResponseBase.STATUS_BAD_GATEWAY)

            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )
        except Exception as e:
            # Response final
            response.set_data({"params": None, "data": None})
            response.set_message("Lấy dữ liệu không thành công!")
            response.add_error({"code": 00, "message": str(e)})
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            logger_bug_sys.warning(
                request,
                ResponseBase.STATUS_BAD_REQUEST,
                "GET_check_edit_nhanmau",
                f"GET_check_edit_nhanmau: {str(e)}",
            )
            return Response(
                data=response.return_response()["data_response"],
                status=response.return_response()["status_response"],
            )

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    @action(methods=["post"], detail=False, url_path="ghinhan-trangthai", name="")
    def PRIV_POST_update_trangthai_dvyeucau(self, request):
        # init response
        response = ResponseBase()
        try:
            if request.user.is_anonymous:
                response.set_data(None)
                response.set_message("Xác thực người dùng hết hạn!")
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

            # data body
            data_body = request.data

            try:
                with transaction.atomic(using="default"):
                    ghinhan = GhiNhanMauXetNghiem()

                    # asign value
                    ghinhan = assign_fields_to_instance(
                        instance=ghinhan,
                        data=data_body,
                        exclude_fields=["files_infor", "file", "fileinformation"],
                        response=response,
                    )
                    ghinhan.save()

                    # return response
                    data_response = GhiNhanMauXetNghiemSerializer(ghinhan).data
                    response.set_data(data_response)
                    response.set_message("Tạo nhiều nguồn file thành công!")
                    response.set_status(ResponseBase.STATUS_CREATED)
            except Exception as e:
                # Exception Set Data
                response.set_data(None)
                response.set_message("Lỗi!")
                response.add_error({"server": str(e)})
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Tạo nguồn file không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            response.add_error({"server": str(e)})

        return Response(
            data=response.return_response()["data_response"],
            status=response.return_response()["status_response"],
        )
