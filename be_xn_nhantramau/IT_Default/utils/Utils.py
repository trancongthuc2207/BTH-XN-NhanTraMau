import re
from .CodeGenerate import *
from django.utils.timezone import now
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import qrcode
from ..models import *
from general_utils.ResponseBase import ResponseBase
from rest_framework.views import Response
from rest_framework import status
from general_utils.utils import split_and_clean, remove_duplicates
from django.db.models import Q
from ..management.commands.command_util import run_command_in_background
from general_utils.banking import VietQRGenerator
import unicodedata
import mimetypes


# ---------------------------- #
# ---------------------------- #
# ---------- CHECK ----------- #
# ---------------------------- #
# ---------------------------- #


def is_valid_email(email):
    # Define the regex pattern for validating an email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None
