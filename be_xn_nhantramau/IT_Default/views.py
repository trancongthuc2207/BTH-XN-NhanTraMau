from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import Response
from .models import *
from .serializers import *
from datetime import datetime
from .throttles import *
import math
from django.conf import settings
import random
import string

# ViewSet
from .viewsets.DefaultViewSets import *
from .viewsets.PUB.XN_DVYeuCauViewSets import *

# ------- Default ------- #
DefaultViewSet = DefaultViewSetBase

# ------- XN_DVYeuCauViewSets ------- #
XN_DVYeuCauViewSet = XN_DVYeuCauSetBase
