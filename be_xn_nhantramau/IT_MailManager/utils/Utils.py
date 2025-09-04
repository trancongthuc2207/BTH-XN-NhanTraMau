import re
from typing import Dict, Optional, Tuple

from IT_FilesManager.models import *
from IT_FilesManager.serializers import *

from IT_MailManager.models import ConfigApp as ConfigAppMail

# Utils
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelper, LogHelperOnlyString
from general_utils.utils import *
from general_utils.GetConfig.UtilsConfigSystem import GET_VALUE_ACTION_SYSTEM

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")

logger_bug_string_sys = LogHelperOnlyString("file_bug_sys")
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


# Kiểm tra các file trên server trước khi gửi mail
def CHECK_LIST_ID_FILES_ON_SERVER_BEFORE_SEND(list_id: list) -> tuple:
    """
    Checks if a list of files exists in the database and on the server.

    Args:
        list_id (list): A list of primary keys (IDs) of the Files objects to check.

    Returns:
        tuple: A tuple (success, list_errors).
               - success (bool): True if all files are valid and exist, False otherwise.
               - list_errors (list): A list of strings containing error messages.
    """
    list_errors = []

    # 1. Kiểm tra các file có tồn tại trong database không
    files_queryset = Files.objects.using("default").filter(pk__in=list_id)
    files_found_ids = [file.pk for file in files_queryset]

    # Tìm các ID không tồn tại trong database
    not_found_ids = [
        file_id for file_id in list_id if file_id not in files_found_ids]
    for file_id in not_found_ids:
        list_errors.append(
            f"File ID {file_id} này không tìm thấy trên hệ thống dữ liệu.")

    # 2. Kiểm tra các điều kiện khác trên các file đã tìm thấy
    for file_obj in files_queryset:
        # Kiểm tra trường file có null không
        if not file_obj.file:
            list_errors.append(
                f"File '{file_obj.file_name}' (ID: {file_obj.pk}) đang không có đường dẫn.")
            continue

        # Kiểm tra trạng thái is_error
        if file_obj.is_error:
            list_errors.append(
                f"File '{file_obj.file_name}' (ID: {file_obj.pk}) được đánh dấu đang gặp lỗi!")

        # Kiểm tra sự tồn tại vật lý của file trên server
        if not file_obj.file.storage.exists(file_obj.file.name):
            list_errors.append(
                f"File '{file_obj.file_name}' (ID: {file_obj.pk}) không tồn tại file trên máy chủ.")

        # Convert 20 MB to bytes
        MAX_UPLOAD_SIZE, NUM_MB = GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD()
        if file_obj.file.size > MAX_UPLOAD_SIZE:
            # Format the size in MB for the error message
            file_size_mb = file_obj.file.size / (1024 * 1024)
            list_errors.append(
                f"File '{file_obj.file_name}' (ID: {file_obj.pk}) có dung lượng {file_size_mb:.2f} MB, vượt quá {NUM_MB} MB cho phép."
            )
    # Trả về kết quả
    is_success = not bool(list_errors)
    return is_success, list_errors, files_queryset


# Chuyển đổi file sang Base64 => truyền địa chỉ file , output là Base64
def get_base64_from_file(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Reads a file from the given path and converts its content to a Base64 encoded string.

    Args:
        file_path (str): The full path to the file to be converted.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the Base64 string and
        an error message. If successful, the Base64 string is returned and the
        error is None. Otherwise, None is returned for the Base64 string, and
        an error message is provided.
    """
    # 1. Check if the file path is valid and the file exists on the server
    if not file_path or not os.path.exists(file_path):
        return None, f"File not found on server at path: {file_path}"

    # 2. Read the file content in binary mode and convert to Base64
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
            encoded_content = base64.b64encode(file_content)
            # Decode bytes to a UTF-8 string before returning
            return encoded_content.decode('utf-8'), None

    except Exception as e:
        return None, f"An error occurred while encoding the file to Base64: {e}"


# Dung lượng file upload tối đa theo config
def GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD():
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB

    try:
        config = GET_VALUE_ACTION_SYSTEM(
            ConfigAppMail, "MAXIMUM_FILE_DATA_FOR_UPLOAD_SEND_MAIL", "default")
        if config:
            MAX_UPLOAD_SIZE = int(config) * 1024 * 1024
        else:
            logger_bug_string_sys.warning(ResponseBase.STATUS_BAD_REQUEST, "GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD::ERROR",
                                          f"Chưa cấu hình tham số 'MAXIMUM_FILE_DATA_FOR_UPLOAD_SEND_MAIL'")
    except Exception as e:
        print(f"GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD: {str(e)}")
        # Logging
        logger_bug_string_sys.warning(ResponseBase.STATUS_BAD_REQUEST, "GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD::ERROR",
                                      f"{str(e)}")

    max_bytes = MAX_UPLOAD_SIZE
    num_mb = max_bytes / 1024 / 1024
    return max_bytes, num_mb
