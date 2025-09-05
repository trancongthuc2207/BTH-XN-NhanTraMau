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
# from IT_OAUTH.models import *
from IT_FilesManager.enums.default_enum import *
from IT_Default.models import ConfigApp as ConfigAppDefault
from IT_FilesManager.paginations import Paginations
from IT_FilesManager.perms import *
from IT_FilesManager.queries import Queries
from IT_FilesManager.serializers import *
from IT_OAUTH.throttles import *
from IT_FilesManager.utils.Utils import *

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.utils import *
from general_utils.Logging.logging_tools import LogHelper
from general_utils.GetConfig.UtilsConfigSystem import *

from IT_Default.utils.sql_server.sql_utils import sql_build_advanced_filters_and_pagination

# External/Internal OAuth App
from IT_OAUTH.serializers import *

# Serializers
from IT_FilesManager.Serializers import (
    FilesSerializers
)

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

    @action(methods=["get"], detail=False, url_path="nhan-mau/all", name="")
    def GET_danhsach_dichvu_yeucau_xn_all(self, request):
        try:
            # init response
            response = ResponseBase()

            filters, pagination, params = sql_build_advanced_filters_and_pagination(
                request, exclude_filter=["join_information_file_value"])

            print(filters)
            print(pagination)
            print(params)

            str_sql = GET_VALUE_ACTION_SYSTEM(
                ConfigAppDefault, "SQL_DS_DVYC_ALL", "default")
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
                }
            )
            # print(result)
            # Response final
            response.set_data({
                "params": params,
                "pagination": pagination,
                # "count": paginator.count,
                # "total_pages": paginator.num_pages,
                "current_page": pagination["page"],
                "infor_more": infor_more,
                "data": result.data
            })
            response.set_message(result.message)
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
                "infor_more": None,
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
            logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "GET_danhsach_dichvu_yeucau_xn_all",
                                   f"GET_danhsach_dichvu_yeucau_xn_all: {str(e)}")
            return Response(data=response.return_response()["data_response"], status=response.return_response()["status_response"])

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
