import re
from IT_FilesManager.models import *
from IT_FilesManager.serializers import *

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelper

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")
# ---------------------------- #
# ---------------------------- #
# ---------- CHECK ----------- #
# ---------------------------- #
# ---------------------------- #


def is_valid_email(email):
    # Define the regex pattern for validating an email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def DICTIONARY_FILE_INFOR(request):
    data_map = []
    try:
        # Dictionary map
        q_dictionary = Dictionary.objects.using("default").filter(
            type="DICTIONARY_FILE_INFOR").order_by("sort_index")
        data_map = DictionaryKeyValueSerializer(
            q_dictionary, many=True).data
    except Exception as e:
        print(f"DICTIONARY_FILE_INFOR: {str(e)}")
        # Logging
        logger_bug_sys.warning(request, ResponseBase.STATUS_BAD_REQUEST, "DICTIONARY_FILE_INFOR",
                               f"{str(e)}")
    return data_map
