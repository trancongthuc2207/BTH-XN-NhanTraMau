from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import Response
from .models import *
from .serializers import *
from datetime import datetime
import math
from django.conf import settings
import random
import string
from django.db import connections
# ViewSet
from .viewsets.UserViewSets import *
from .viewsets.AccessTokenViewSets import *
from .viewsets.ApplicationViewSets import *
from .viewsets.DefaultViewSets import *

# ------- USER ------- #
UserView = UserViewSet

# ------- Access Token ------- #
AccessTokenView = AccessTokenViewSet

ApplicationView = ApplicationViewSet

# ------- Default ------- #
DefaultView = DefaultViewSetBase
