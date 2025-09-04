from general_utils.utils import *
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.conf import settings
from IT_OAUTH.utils.Utils import GET_VALUE_ACTION_SYSTEM


class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.META.get('HTTP_LANGUAGE', 'vn')
        request.language = language
        response = self.get_response(request)
        response['Access-Control-Allow-Private-Network'] = "true"
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "*"
        return response


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        EXCLUDED_BODY_PATHS = split_and_clean(
            GET_VALUE_ACTION_SYSTEM("SET_URL_API_NO_LOGGING"), "||")

        path = request.path
        request_body_str = ""
        should_log_body = (
            request.method != "GET" and not is_contains_api_pattern(
                path, EXCLUDED_BODY_PATHS)
        )

        if should_log_body:
            try:
                body = request.body
                if body:
                    raw_body = body.decode("utf-8", errors="ignore")
                    request_body_str = clean_request_body(raw_body)
            except Exception as e:
                request_body_str = f"[Could not decode body: {e}]"

        response = self.get_response(request)

        return response


class CustomErrorPagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

            if not settings.CONFIG.DEBUG_MODE:
                if response.status_code == 400:
                    return render(request, "400.html", status=400)
                elif response.status_code == 403:
                    return render(request, "403.html", status=403)
                elif response.status_code == 404:
                    return render(request, "404.html", status=404)

            return response

        except Exception as e:
            if not settings.CONFIG.DEBUG_MODE:
                # Optional: Log the exception
                return render(request, "500.html", status=500)
            raise  # Re-raise exception to show Django's detailed error page in DEBUG mode
