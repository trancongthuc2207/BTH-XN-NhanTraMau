# accounts/middleware.py
import logging
import threading
import fnmatch
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.http import JsonResponse  # Import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import *
from general_utils.utils import *
from general_utils.GetConfig.UtilsConfigSystem import GET_VALUE_ACTION_SYSTEM


logger = logging.getLogger(__name__)


class OAuth2TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.User = get_user_model()

    def __call__(self, request):
        # A more robust check for API requests
        is_api_request = (
            request.path.startswith('/api/priv') or
            request.path.startswith('/oauth/') or
            'application/json' in request.META.get('HTTP_ACCEPT', '') or
            'application/xml' in request.META.get('HTTP_ACCEPT', '')
        )

        if is_api_request:
            # Apply token authentication logic
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')

            if auth_header.startswith('Bearer '):
                token_value = auth_header.split(' ')[1]
                try:
                    access_token = AccessToken.objects.select_related('user').get(
                        access_token=token_value,
                        active=True,
                        expires_at__gt=timezone.now()
                    )
                    request.user = access_token.user
                    request.access_token = access_token
                except AccessToken.DoesNotExist:
                    logger.warning(
                        f"Invalid or expired access token: {token_value}")
                    # For API requests, return 401 Unauthorized immediately if token is invalid
                    # This prevents the request from proceeding to views that expect a user
                    return JsonResponse({'error': 'invalid_token', 'error_description': 'Access token is invalid or expired.'}, status=401)
                except Exception as e:
                    logger.error(
                        f"Error in OAuth2TokenAuthenticationMiddleware: {e}")
                    return JsonResponse({'error': 'server_error', 'error_description': 'An internal server error occurred during authentication.'}, status=401)
            else:
                # If it's an API request but no Bearer token, return 401
                # unless you have other authentication methods for your API
                # Check if user is already authenticated by session etc.
                if not request.user.is_authenticated:
                    return JsonResponse({'error': 'unauthorized', 'error_description': 'Authentication required. Bearer token missing.'}, status=401)

        # For non-API requests or if token authentication passed, continue
        response = self.get_response(request)
        return response


# ----------------  LOGGING RESPONSE ----------------- #

# Hàm giả định để lấy địa chỉ IP của client
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def contains_api_pattern(path, list_check):
    for pattern in list_check:
        if fnmatch.fnmatch(path, pattern):
            return True

    # If no exceptions match, check for the 'api' pattern
    return False


def log_response_in_thread(status_code, path, user, method, response_content, response_size, ip_address):
    """
    Hàm này sẽ được chạy trong một luồng riêng để ghi log.
    Nó tách biệt hoàn toàn khỏi luồng chính của request.
    """
    try:
        # Config in DB
        list_url_api_check_more = []
        list_status_code_logging = []

        # Tránh ghi log cho các request
        if GET_VALUE_ACTION_SYSTEM(ConfigApp, "LIST_URL_PATH_EXCEPT_RESPONSE_LOGGING"):
            list_url_api_check_more = split_and_clean(
                GET_VALUE_ACTION_SYSTEM(ConfigApp, "LIST_URL_PATH_EXCEPT_RESPONSE_LOGGING"), "||")
            if contains_api_pattern(path, list_url_api_check_more):
                return

        if GET_VALUE_ACTION_SYSTEM(ConfigApp, "LIST_STATUS_CODE_RESPONSE_LOGGING"):
            list_status_code_logging = split_and_clean(
                GET_VALUE_ACTION_SYSTEM(ConfigApp, "LIST_STATUS_CODE_RESPONSE_LOGGING"), "||")
            if not contains_api_pattern(str(status_code), list_status_code_logging):
                return

        ResponseLog.objects.create(
            status_code=status_code,
            path=path,
            user=user,
            method=method,
            response_size=response_size,
            ip_address=ip_address,
            content=response_content
        )
    except Exception as e:
        # Quan trọng: Ghi log lỗi nếu quá trình lưu log thất bại
        # để bạn có thể xem xét sau này.
        print(f"Lỗi khi ghi log phản hồi: {e}")


class ResponseLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """
        Ghi lại thông tin phản hồi bất đồng bộ sau khi request được xử lý.
        """

        if response.status_code:
            try:
                # Lấy kích thước của phản hồi
                response_size = len(response.content)
            except (AttributeError, TypeError):
                response_size = None

            response_content = None
            try:
                # Chuyển đổi nội dung byte thành chuỗi
                response_content = response.content.decode('utf-8', 'ignore')
                # Cắt bớt nội dung nếu nó quá dài
                if len(response_content) > 10000:
                    response_content = response_content[:10000] + "..."
            except Exception:
                response_content = None

            # Bắt đầu một luồng riêng biệt để thực hiện việc ghi log
            # Tham số được truyền vào hàm phải được bọc trong một tuple
            thread_args = (
                response.status_code,
                request.path,
                request.user if request.user.is_authenticated else None,  # Ghi ID người dùng
                request.method,
                response_content,
                response_size,
                get_client_ip(request)
            )

            # Khởi tạo và chạy luồng
            threading.Thread(target=log_response_in_thread,
                             args=thread_args).start()

        # Trả lại response ngay lập tức, không chờ luồng ghi log hoàn thành
        return response
