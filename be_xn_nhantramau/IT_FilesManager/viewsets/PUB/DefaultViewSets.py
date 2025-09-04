from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response, APIView
from IT_FilesManager.models import *
from IT_FilesManager.serializers import *
from datetime import datetime
from IT_OAUTH.throttles import *
from django.conf import settings
from django.shortcuts import render
from IT_FilesManager.utils.ResponseMessage import *
from IT_FilesManager.perms import *
from IT_FilesManager.utils.CodeGenerate import *
from IT_OAUTH.models import User
from IT_OAUTH.serializers import *
from IT_FilesManager.paginations import Paginations
from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

# Config
from IT_OAUTH.models import ConfigApp as ConfigAppOAuth

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelper
from general_utils.utils import *
from general_utils.GetConfig.UtilsConfigSystem import (
    GET_VALUE_ACTION_SYSTEM,
    GET_VALUE_BASE64_ACTION_SYSTEM,
    CHECK_ACTION_SYSTEM,
    BOOL_CHECK_ACTION_SYSTEM,
)

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")

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

        response["data"] = {
            "ds_khoaphong": "this is a placeholder for the list of departments",
        }
        response["message"] = "Successfully retrieved the list of departments."
        response["status_code"] = 200

        return Response(response, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["post"], detail=False, url_path="hash/create", name="")
    def POST_create_hash_password(self, request):
        # init response
        response = ResponseBase()
        try:
            prefix = "pbkdf2_sha256$0e0ac3288f01261829d359a3b3c58dc2$"
            if GET_VALUE_ACTION_SYSTEM(
                ConfigAppOAuth, "PREFIX_CHECK_FILE_DEFAULT", dbname="oauth"
            ):
                prefix = GET_VALUE_ACTION_SYSTEM(
                    ConfigAppOAuth, "PREFIX_CHECK_FILE_DEFAULT", dbname="oauth"
                )

            data_body = request.data
            str_hash = encode_with_prefix(
                input_text=data_body["str_raw"], prefix=prefix
            )

            # return response
            response.set_data({"str_raw": data_body["str_raw"], "str_hash": str_hash})
            response.set_message("Tạo thành công!")
            response.set_status(ResponseBase.STATUS_CREATED)
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Tạo không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            response.add_error({"error": str(e)})

        return Response(
            data=response.return_response()["data_response"],
            status=response.return_response()["status_response"],
        )
