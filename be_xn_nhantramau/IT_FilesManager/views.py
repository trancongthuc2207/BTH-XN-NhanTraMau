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
# PUB
from .viewsets.PUB.DefaultViewSets import *
from .viewsets.PUB.DictionanyViewSets import *
from .viewsets.PUB.FileCategoryViewSets import *
from .viewsets.PUB.FileTypeViewSets import *
from .viewsets.PUB.FilesViewSets import *
# PRIV
from .viewsets.PRIV.PRIV_FileCategoryViewSets import *
from .viewsets.PRIV.PRIV_FileTypeViewSets import *
from .viewsets.PRIV.PRIV_FilesViewSets import *

# --------------------------------------------- #
# -------------------- PUB -------------------- #
# --------------------------------------------- #

# ------- Default ------- #
DefaultViewSet = DefaultViewSetBase
# ------ Dictionary ----- #
DictionanyViewSet = DictionanyViewSetBase
# ----- FileCategory ---- #
FileCategoryViewSet = FileCategoryViewSetBase
# ----- FileType ---- #
FileTypeViewSet = FileTypeViewSetBase
# ----- Files ---- #
FilesViewSet = FilesViewSetBase

# --------------------------------------------- #
# -------------------- PRIV ------------------- #
# --------------------------------------------- #
# ----- PRIV FileCategory ---- #
PRIV_FileCategoryViewSet = PRIV_FileCategoryViewSetBase
# ----- PRIV FileType ---- #
PRIV_FileTypeViewSet = PRIV_FileTypeViewSetBase
# ----- PRIV Files ---- #
PRIV_FilesViewSet = PRIV_FilesViewSetBase
