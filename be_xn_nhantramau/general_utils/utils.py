from typing import Union, BinaryIO
import io
import tempfile
from datetime import datetime, time
import re
import base64
import fnmatch
import hashlib
import os
import json
from typing import List
from django.db import models
from django.utils.dateparse import parse_date, parse_datetime
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.template import Template, Context
from django.template.exceptions import TemplateSyntaxError


def format_vnd(amount):
    try:
        return f"{int(float(amount)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Invalid amount"


def is_valid_email(email):
    # Define the regex pattern for validating an email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Custom function to convert model instance to dictionary


def class_to_custom_dict(instance):
    opts = instance._meta
    data = {}
    for field in opts.concrete_fields:
        data[field.name] = field.value_from_object(instance)
    return data


def is_valid_date(date_str):
    try:
        # Try to convert the string to a date object using the expected format
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        # If there's a ValueError, the format is incorrect
        return False


def convert_to_datetime(date_string):
    # List of possible date formats to try
    possible_formats = [
        "%d/%m/%Y %H:%M:%S",  # Format 1: dd/mm/yyyy hh:mm:ss
        "%Y-%m-%d %H:%M:%S",  # Format 2: yyyy-mm-dd hh:mm:ss
        "%d-%m-%Y %H:%M:%S",  # Format 3: dd-mm-yyyy hh:mm:ss
        "%m/%d/%Y %I:%M:%S %p",  # Format 4: mm/dd/yyyy hh:mm:ss AM/PM
    ]

    for date_format in possible_formats:
        try:
            # Attempt to convert the string to a datetime object
            date_object = datetime.strptime(date_string, date_format)
            return date_object
        except ValueError:
            # If it fails, continue to the next format
            continue

    # If none of the formats work, print a custom error message and return None
    print(
        f"Error: The date string '{date_string}' does not match any of the expected formats."
    )
    return None


# WRITE LOG
def write_log(instance, request):
    try:
        ip_address = request.META.get("REMOTE_ADDR")
        session_key = request.session.session_key
        instance.modified_by = request.user
        instance.ip_address = ip_address
        instance.session_key = session_key
        return instance
    except Exception as e:
        print(str(e))
        return instance


def clean_html_string(html_string):
    # Remove escape sequences like \n, \t, and \"
    cleaned = re.sub(r'\\[ntr"]', "", html_string)
    # Remove redundant whitespaces between HTML tags
    cleaned = re.sub(r">\s+<", "><", cleaned)
    # Normalize multiple spaces to a single space
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    # Strip leading and trailing whitespace
    return cleaned.strip()


def unescape_quotes(html_string):
    # Replace escaped double quotes (\") with regular quotes (")
    return html_string.replace(r"\"", '"')


# Example function to handle the splitting and filtering
def split_and_clean(input_string, character=";;"):
    if not input_string:
        return []
    # Split by ;; and filter out empty strings and None values
    return [x for x in input_string.split(character) if x and x.strip()]


def image_to_base64(image_file):
    """Convert an uploaded image (InMemoryUploadedFile) to a Base64 string."""
    if not image_file:
        return None  # Handle case where no image is uploaded

    try:
        return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error converting image: {e}")
        return None


def remove_duplicates(input_list):
    """
    Remove duplicates from a list while preserving order.

    Args:
        input_list (list): List of strings or items.

    Returns:
        list: A new list with duplicates removed.
    """
    seen = set()
    unique_list = []
    for item in input_list:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list


def format_vietnamese_date(dt: datetime, option=1):
    vietnamese_weekdays = {
        0: "Thứ Hai",
        1: "Thứ Ba",
        2: "Thứ Tư",
        3: "Thứ Năm",
        4: "Thứ Sáu",
        5: "Thứ Bảy",
        6: "Chủ Nhật"
    }
    weekday = dt.weekday()  # Monday is 0, Sunday is 6
    # Adjust for Sunday
    weekday_vn = vietnamese_weekdays[weekday] if weekday < 6 else "Chủ Nhật"

    optine_return = {
        1: f"{dt.strftime('%d/%m/%Y')} ({weekday_vn})",
        2: f"{weekday_vn}, {dt.strftime('%d/%m/%Y')}",
    }
    return optine_return[option]


def clean_request_body(raw: str) -> str:
    """
    Cleans raw multipart/form-data text by removing excessive blank lines and trimming whitespace.
    """
    lines = raw.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip() != ""]
    return "\n".join(cleaned_lines)


def is_contains_api_pattern(path, list_check):
    for pattern in list_check:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


# Tạo bộ lọc nâng cao và phân tích
def build_advanced_filters_and_pagination(request, model, exclude_filter=None):
    if exclude_filter is None:
        exclude_filter = []

    filters = {}
    pagination = {
        "page": 1,
        "limit": 10,
        "ordering": None
    }
    params = {}

    for param_key, value in request.query_params.items():
        params[param_key] = value

        # Skip parameters that are in the exclude list
        if param_key in exclude_filter:
            continue

        if value in ["", None]:
            continue

        # Extract pagination and ordering
        if param_key == "page":
            try:
                pagination["page"] = int(value)
            except ValueError:
                pass
            continue

        if param_key == "limit":
            try:
                pagination["limit"] = int(value)
            except ValueError:
                pass
            continue

        if param_key == "ordering":
            pagination["ordering"] = value
            continue

        # Date filters
        if param_key.startswith("from_"):
            field_name = param_key[5:]
            parsed_date = parse_datetime(value) or parse_date(value)
            if parsed_date:
                filters[f"{field_name}__gte"] = parsed_date
            continue

        if param_key.startswith("to_"):
            field_name = param_key[3:]
            parsed_date = parse_datetime(value) or parse_date(value)

            if parsed_date:
                # If the parsed_date is a date (not datetime), set it to the end of the day
                if isinstance(parsed_date, datetime):
                    filters[f"{field_name}__lte"] = parsed_date
                else:
                    filters[f"{field_name}__lte"] = datetime.combine(
                        parsed_date, time.max)
            continue

        # General filters
        top_field = param_key.split("__")[0]
        try:
            field = model._meta.get_field(top_field)
        except Exception:
            filters[param_key] = value
            continue

        if isinstance(field, models.ForeignKey) and "__" in param_key:
            filters[param_key] = value
        elif isinstance(field, models.JSONField):
            filters[param_key] = value
        elif isinstance(field, (models.CharField, models.TextField)):
            filters[f"{param_key}__icontains"] = value
        elif isinstance(field, models.BooleanField):
            filters[param_key] = value.lower() in ['true', '1', 'yes']
        elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
            try:
                filters[param_key] = type(field)().to_python(value)
            except Exception:
                pass
        elif isinstance(field, (models.DateTimeField, models.DateField)):
            parsed = parse_datetime(value) or parse_date(value)
            if parsed:
                filters[param_key] = parsed
        else:
            filters[param_key] = value

    return filters, pagination, params


# Gắn dữ liệu vào model
def assign_fields_to_instance(instance, data, exclude_fields=None, response=None):
    """
    Assign request.data to Django model instance with type casting and error tracking.
    """
    exclude_fields = exclude_fields or []

    # === VERIFY THIS LINE IS EXACTLY AS SHOWN ===
    model = instance.__class__
    # === END VERIFICATION ===

    field_map = {field.name: field for field in model._meta.get_fields()}

    for key, value in data.items():
        if key in exclude_fields:
            continue

        if isinstance(value, InMemoryUploadedFile) and not (key in field_map and isinstance(field_map[key], models.FileField)):
            continue

        if key not in field_map:
            if response and hasattr(response, "add_entities_error"):
                response.add_entities_error({
                    "field": key,
                    "message": f"Trường '{key}' không tìm thấy trong mô hình."
                })
            continue

        field = field_map[key]

        try:
            if isinstance(field, models.ForeignKey):
                rel_model = field.related_model
                if value is None or value == "":
                    setattr(instance, key, None)
                else:
                    try:
                        related_instance = rel_model.objects.get(pk=value)
                        setattr(instance, key, related_instance)
                    except ObjectDoesNotExist:
                        raise ValueError(
                            f"{rel_model.__name__} với ID={value} không tồn tại.")
            elif isinstance(field, models.BooleanField):
                if isinstance(value, bool):
                    setattr(instance, key, value)
                else:
                    setattr(instance, key, str(value).lower()
                            in ["true", "1", "yes"])
            elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
                setattr(instance, key, field.to_python(value))
            elif isinstance(field, (models.DateTimeField, models.DateField)):
                parsed_date = None
                if isinstance(value, str):
                    parsed_date = parse_datetime(value) or parse_date(value)
                elif isinstance(value, (datetime, datetime.date)):
                    parsed_date = value
                if parsed_date:
                    setattr(instance, key, parsed_date)
                else:
                    raise ValueError(
                        f"Định dạng ngày/thời gian không hợp lệ cho trường '{key}'.")
            elif isinstance(field, models.FileField) and isinstance(value, InMemoryUploadedFile):
                setattr(instance, key, value)
            else:
                setattr(instance, key, value)
        except Exception as e:
            if response and hasattr(response, "add_entities_error"):
                response.add_entities_error({
                    "field": key,
                    "message": str(e)
                })

    return instance


def create_password_hash(password, salt=None):
    if not salt:
        salt = os.urandom(16).hex()

    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')

    hashed_password = hashlib.pbkdf2_hmac(
        'sha256', password_bytes, salt_bytes, 100000)

    return f"pbkdf2_sha256${salt}${hashed_password.hex()}"


def check_password_hash(plain_password, stored_password):
    try:
        algorithm, salt, hashed = stored_password.split('$')

        password_bytes = plain_password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')

        hashed_password = hashlib.pbkdf2_hmac(
            algorithm.split('_')[1], password_bytes, salt_bytes, 100000)

        return hashed_password.hex() == hashed
    except ValueError:
        return False


# ================================================================= #

def add_prefix(input_string, prefix):
    """Adds a prefix to a string if it's not already there."""
    if not input_string.startswith(prefix):
        return prefix + input_string
    return input_string


def remove_prefix(input_string, prefix):
    """Removes a prefix from a string if it exists."""
    if input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string


def encode_with_prefix(input_text: str, prefix: str) -> str:
    """
    Encodes the input text to Base64, adds a prefix, then encodes to Base64 again.

    Args:
        input_text (str): The text string to encode.
        prefix (str): The prefix to add before the second encoding.

    Returns:
        str: The final double-Base64 encoded string.
    """
    # Step 1: Encode the input text to Base64
    text_bytes = input_text.encode('utf-8')
    encoded_text = base64.b64encode(text_bytes).decode('utf-8')

    # Step 2: Add the prefix to the first encoded string
    prefixed_encoded_text = add_prefix(encoded_text, prefix)

    # Step 3: Encode the prefixed string to Base64 again
    final_bytes = prefixed_encoded_text.encode('utf-8')
    final_encoded = base64.b64encode(final_bytes)
    return final_encoded.decode('utf-8')


def decode_with_prefix(encoded_string: str, prefix: str) -> str:
    """
    Decodes a double-Base64 string, removes the prefix, then decodes again.

    Args:
        encoded_string (str): The final Base64 encoded string.
        prefix (str): The prefix to remove after the first decoding.

    Returns:
        str: The original text string.

    Raises:
        ValueError: If the decoded string is not in the correct format.
    """
    try:
        # Step 1: Decode the final Base64 string
        decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
        decoded_text_with_prefix = decoded_bytes.decode('utf-8')

        # Step 2: Remove the prefix
        encoded_text_without_prefix = remove_prefix(
            decoded_text_with_prefix, prefix)

        # Step 3: Decode the remaining Base64 string to get the original text
        original_bytes = base64.b64decode(
            encoded_text_without_prefix.encode('utf-8'))
        return original_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid Base64 string in decoding process: {e}")


def add_extra_conditions_to_queryset(queryset, extra_params=None):
    """
    Applies additional, more complex filter conditions to an existing queryset.

    This is useful for adding Q object-based filters (e.g., OR conditions)
    after the initial, simple filters have been applied.

    Args:
        queryset: An existing Django queryset.
        extra_params (dict, optional): A dictionary of additional filters to apply.
                                       Defaults to None.

    Returns:
        The modified queryset with the new conditions applied.
    """
    if extra_params:
        # A more generic and flexible approach to filtering with joins.
        # This now supports using either `related_name` or `model_join` to specify the join.
        if 'joins' in extra_params and isinstance(extra_params['joins'], list):
            for join_config in extra_params['joins']:
                related_name = join_config.get('related_name')
                model_to_join = join_config.get('model_join')
                conditions = join_config.get('conditions', {})

                if conditions and (related_name or model_to_join):
                    # If a model class is provided, find the related_name dynamically
                    if model_to_join:
                        try:
                            # Search the target model's fields for a ForeignKey pointing back to the queryset model
                            for field in model_to_join._meta.get_fields():
                                if field.is_relation and field.related_model == queryset.model:
                                    related_name = field.related_query_name()
                                    break
                        except AttributeError:
                            pass

                    if related_name:
                        # Construct the filter dictionary using the provided keys,
                        # allowing for explicit lookups like 'value__icontains'.
                        q_filters = {
                            f"{related_name}__{k}": v for k, v in conditions.items()
                        }
                        queryset = queryset.filter(**q_filters)

    return queryset


# Trích xuất các biến từ mẫu HTML
def extract_template_variables(html_template: str) -> List[str]:
    """
    Trích xuất tất cả các biến placeholder từ một chuỗi mẫu HTML.

    Args:
        html_template (str): Chuỗi HTML chứa các biến ở định dạng {{ var_name }}.

    Returns:
        List[str]: Một danh sách các tên biến duy nhất đã được trích xuất.
    """
    # Regex pattern để tìm các chuỗi có định dạng {{...}}
    # (.*?) là một nhóm bắt (capturing group) để lấy nội dung bên trong,
    # ? làm cho nó không tham lam (non-greedy), chỉ khớp với đoạn ngắn nhất.
    pattern = r"\{\{\s*(.*?)\s*\}\}"

    # re.findall tìm tất cả các chuỗi khớp với pattern và trả về nội dung của nhóm bắt
    variables = re.findall(pattern, html_template, re.IGNORECASE)

    # Trả về một danh sách các biến duy nhất
    return list(set(variables))


def extract_cid_variables(html_template: str) -> list[str]:
    """
    Trích xuất tất cả các biến CID (Content-ID) từ một chuỗi mẫu HTML.

    Args:
        html_template (str): Chuỗi HTML có chứa các biến ở định dạng cid:tencid.

    Returns:
        List[str]: Một danh sách các tên CID duy nhất đã được trích xuất.
    """
    # Regex pattern để tìm các chuỗi có định dạng cid:tencid
    # (.*?) là một nhóm bắt (capturing group) để lấy nội dung bên trong.
    # ? làm cho nó không tham lam (non-greedy), chỉ khớp với đoạn ngắn nhất.
    pattern = r"cid:(\w+)"

    # re.findall tìm tất cả các chuỗi khớp với pattern và trả về nội dung của nhóm bắt.
    variables = re.findall(pattern, html_template, re.IGNORECASE)

    # Trả về một danh sách các biến duy nhất.
    return list(set(variables))

######################################################################################
# XỬ LÝ FILE
######################################################################################

# Ghi chú: Sử dụng tempfile.mkstemp() thay vì NamedTemporaryFile()
# để đảm bảo tệp tin không bị xóa khi nó vẫn đang được sử dụng.
# Tệp tin vẫn sẽ tồn tại sau khi hàm này kết thúc.


def create_temp_file(data: Union[str, bytes, BinaryIO], file_name: str = None) -> str:
    """
    Creates a temporary file from various data types and returns its path.
    The function handles Base64 strings, byte streams, and file-like objects.

    Args:
        data (Union[str, bytes, BinaryIO]): The input data.
            - If it's a str, it's assumed to be Base64 encoded and will be decoded.
            - If it's bytes, it will be written directly.
            - If it's a file-like object (e.g., from request.FILES), its content will be read.
        file_name (str, optional): A suggested name for the file.
                                   The function will append a unique suffix to avoid conflicts.

    Returns:
        str: The full path to the created temporary file.

    Raises:
        TypeError: If the input data type is not supported.
    """

    # Check if data is valid before proceeding
    if not data:
        raise TypeError("Input data is empty or None.")

    # Create a temporary file with a unique name
    if file_name and isinstance(file_name, str):
        # Get the file extension from the suggested file name
        _, ext = os.path.splitext(file_name)
        # Check if an extension exists before using it
        if ext:
            fd, path = tempfile.mkstemp(suffix=ext)
        else:
            fd, path = tempfile.mkstemp()
    else:
        # If no file name is provided or it's not a string, use the default naming convention
        fd, path = tempfile.mkstemp()

    try:
        # Get the file object from the file descriptor
        with os.fdopen(fd, 'wb') as temp_file:
            if isinstance(data, str):
                # Check for and remove a common Base64 prefix
                if ',' in data:
                    data = data.split(',', 1)[-1]

                # Data is a Base64 string, decode it
                try:
                    decoded_data = base64.b64decode(data, validate=True)
                    temp_file.write(decoded_data)
                except base64.binascii.Error as e:
                    raise ValueError(f"Invalid Base64 string: {e}")
            elif isinstance(data, bytes):
                # Data is a byte stream, write it directly
                temp_file.write(data)
            elif isinstance(data, io.IOBase):
                # Data is a file-like object, read and write its content
                data.seek(0)
                temp_file.write(data.read())
            else:
                raise TypeError(
                    "Unsupported data type. Must be str, bytes, or a file-like object.")

        return path
    except Exception as e:
        # It's crucial to clean up the temp file if something goes wrong
        if os.path.exists(path):
            os.remove(path)
        raise e


def remove_temp_file(file_path: str):
    """
    Removes a temporary file from the server.

    Args:
        file_path (str): The full path to the temporary file to be removed.
    """
    try:
        # Check if the file exists before trying to remove it
        if os.path.exists(file_path):
            os.remove(file_path)
            # print(f"Successfully removed temporary file: {file_path}")
        else:
            # print(f"File not found, could not remove: {file_path}")
            pass  # Or raise an exception, depending on your needs
    except OSError as e:
        # Handle potential errors, e.g., permission denied
        # print(f"Error removing temporary file {file_path}: {e}")
        raise e


def load_json_from_file(file_path):
    """
    Loads JSON data from a specified file path.

    This function attempts to open and read a file, then parse its
    contents as JSON. It includes robust error handling for common issues
    like file not found or invalid JSON format.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or None: The parsed JSON data as a dictionary if successful,
                      otherwise None.
    """
    try:
        # Use 'with open' to ensure the file is properly closed after use
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the JSON data from the file
            data = json.load(file)
            print(f"Successfully loaded JSON from: {file_path}")
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def render_template_string(template_str: str, context: dict) -> tuple[bool, str]:
    """
    Render a Django template string with context.
    Returns (success, rendered_string).
    """
    try:
        tmpl = Template(template_str)
        rendered = tmpl.render(Context(context))
        return True, rendered.strip()
    except TemplateSyntaxError as e:
        return False, f"Template syntax error: {e}"
    except Exception as e:
        return False, str(e)