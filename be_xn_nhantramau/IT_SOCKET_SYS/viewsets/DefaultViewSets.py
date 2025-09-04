from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response
from ..models import *
from ..serializers import *
from datetime import datetime
from IT_OAUTH.throttles import *
import math
from django.conf import settings
from django.shortcuts import render
from ..utils.ResponseMessage import *
from ..queries import Queries
from ..perms import *
from IT_OAUTH.models import User
from ..paginations import Paginations

# /(?P<id>[a-zA-Z0-9]+)
# Khoa Khám Bệnh


class DefaultViewSetBase(viewsets.ViewSet, ):
    queryset = User.objects.using('oauth').all()
    throttle_classes = [SuperRateThrottle]
    # serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    # Màn hình lấy mẫu của các phòng khám
    @action(methods=['get'], detail=False, url_path='get/ds-khoaphong', name='')
    def get_ds_khoaphong(self, request):
        # init response
        response = {
        }

        # Dieu kien
        where = {
            'sodong': '',
        }

        page_config = {
            'from': 0,
            'amount': Paginations.NUM_PAGES_DEFAULT
        }

        # Set dieu kien
        # sodong = request.query_params.get('sodong')
        # if sodong:
        #    where['sodong'] = sodong

        result = Queries.get_danhsach_khoaphong_nk(where=where, page_config={})
        if result.status == 1:
            response['data'] = result.data
            response['message'] = result.message
            response['result'] = 1
            response['status_code'] = 200
        else:
            response['data'] = result.data
            response['message'] = result.message
            response['result'] = 0
            response['status_code'] = 499

        return Response(response, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------- PUT ------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
