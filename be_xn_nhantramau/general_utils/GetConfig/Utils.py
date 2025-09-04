import re
import base64
from django.db.models import Q
from general_utils.banking import VietQRGenerator
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


def file_to_base64_data_uri(file_obj):
    mime_type, _ = mimetypes.guess_type(file_obj.name)
    base64_str = base64.b64encode(file_obj.read()).decode("utf-8")
    return f"data:{mime_type};base64,{base64_str}"
