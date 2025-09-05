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
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe

# Django REST Framework
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

# Internal Apps
# from IT_OAUTH.models import *
from IT_FilesManager.enums.default_enum import *
from IT_Default.models import ConfigApp as ConfigAppDefault
from IT_OAUTH.models import ConfigApp as ConfigAppOauth
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


class TemplateSetBase(
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

    @action(methods=["get"], detail=False, url_path="login")
    def XN_LOGIN(self, request):
        # init
        LIST_ROLE = []

        get_config = GET_VALUE_ACTION_SYSTEM(
            ConfigAppDefault, "LIST_ROLE_FOR_XN_NHAN_MAU", "default")
        if get_config:
            LIST_ROLE = json.loads(get_config)

        KEY_AUTHOR = "BTHNOIBO"
        get_config_key_author = GET_VALUE_ACTION_SYSTEM(
            ConfigAppOauth, "KEY_AUTHORIZATION", "default")
        if get_config_key_author:
            KEY_AUTHOR = get_config_key_author

        context = {
            "host_be": settings.HOST,
            "KEY_AUTHOR": KEY_AUTHOR,
            "LIST_ROLE": LIST_ROLE,
            "LIST_ROLE_JSON": mark_safe(json.dumps(LIST_ROLE)),
        }
        return TemplateResponse(request, "xn_login/xn_login.html", context)

    @action(methods=["get"], detail=False, url_path="logout")
    def XN_LOGOUT(self, request):
        # init
        context = {
            "host_be": settings.HOST,
        }
        return TemplateResponse(request, "xn_login/xn_logout.html", context)

    @action(methods=["get"], detail=False, url_path="main")
    def XN_LAB_MAIN(self, request):
        # init
        LIST_ROLE = []
        get_config_role = GET_VALUE_ACTION_SYSTEM(
            ConfigAppDefault, "LIST_ROLE_FOR_XN_NHAN_MAU", "default")
        if get_config_role:
            LIST_ROLE = json.loads(get_config_role)

        KEY_AUTHOR = "BTHNOIBO"
        get_config_key_author = GET_VALUE_ACTION_SYSTEM(
            ConfigAppOauth, "KEY_AUTHORIZATION", "default")
        if get_config_key_author:
            KEY_AUTHOR = get_config_key_author

        # init params
        defaultParams = """
        {
        "MAYTE": "",
        "TIEPNHAN_ID": "",
        "FROM_DATE": new Date().toISOString().split('T')[0],
        "TO_DATE": new Date().toISOString().split('T')[0],
        "page": "1",
        "limit": "100",
        "ordering": "-NGAYTAO"
        }
        """
        get_config_params_default = GET_VALUE_ACTION_SYSTEM(
            ConfigAppDefault, "OBJ_PARAMS_SEARCH_XN_ALL", "default")
        if get_config_params_default:
            defaultParams = get_config_params_default
        # print(get_config_params_default)

        # init params labels
        defaultParamsLabels = """
        {
         "MAYTE": "Mã Y Tế",
         "TIEPNHAN_ID": "TIEPNHAN ID",
         "FROM_DATE": "From Date",
         "TO_DATE": "To Date",
         "page": "Page",
         "limit": "Limit",
         "ordering": "Ordering"
        }
        """
        get_config_defaultParamsLabels = GET_VALUE_ACTION_SYSTEM(
            ConfigAppDefault, "OBJ_PARAMS_SEARCH_MAPPING_LABEL_XN_ALL", "default")
        if get_config_defaultParamsLabels:
            defaultParamsLabels = get_config_defaultParamsLabels

        # init tableColumnsLabels
        tableColumnsLabels = """
        {
        "SOPHIEUYEUCAU": "Request No.",
        "TENDICHVU": "Service Name",
        "TENNHOMDICHVU": "Service Group",
        "NGAYGIOYEUCAU": "Request Date",
        "TRANGTHAI": "Status",
        "PHONGBAN_YEUCAU": "Request Dept.",
        "TEN_BS_CD": "Ordering Doctor",
        "TENNHOMDICHVU": "Tên nhóm dịch vụ"
        }
        """
        get_config_defaultTableViewLabels = GET_VALUE_ACTION_SYSTEM(
            ConfigAppDefault, "OBJ_MAPPING_TABLE_COLUMN_XN_ALL", "default")
        if get_config_defaultTableViewLabels:
            tableColumnsLabels = get_config_defaultTableViewLabels

        context = {
            "host_be": settings.HOST,
            "KEY_AUTHOR": KEY_AUTHOR,
            "LIST_ROLE": LIST_ROLE,
            "LIST_ROLE_JSON": mark_safe(json.dumps(LIST_ROLE)),
            "defaultParams": mark_safe(defaultParams),
            "defaultParamsLabels": mark_safe(defaultParamsLabels),
            "tableColumnsLabels": mark_safe(tableColumnsLabels),
        }
        return TemplateResponse(request, "xn_login/xn_lab_main.html", context)

    @action(methods=["get"], detail=False, url_path="admin")
    def XN_ADMIN_PAGE(self, request):
        #
        KEY_AUTHOR = "BTHNOIBO"
        get_config_key_author = GET_VALUE_ACTION_SYSTEM(
            ConfigAppOauth, "KEY_AUTHORIZATION", "default")
        if get_config_key_author:
            KEY_AUTHOR = get_config_key_author

        # init
        today = datetime.now()
        current_date = today.strftime("%Y-%m-%d")

        where = {
            "quaygoi": (
                "Phòng 1 - Quầy 1"
                if not request.query_params.get("quaygoi")
                else request.query_params.get("quaygoi")
            ),
        }

        context = {
            "title": "FPT PLM Main",
            "message": "Hello from Django template!",
            "quaygoi": where["quaygoi"],
            "host_be": settings.HOST,
            "current_date": current_date,
            "KEY_AUTHOR": KEY_AUTHOR,
        }
        return TemplateResponse(request, "xn_admin/xn_admin.html", context)

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
