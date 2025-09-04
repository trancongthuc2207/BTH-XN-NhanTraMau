import json
from datetime import datetime


class LoggingDescription:
    def __init__(self, code, title, content):
        self.code = code
        self.title = title
        self.content = content

    def to_dict(self):
        return {
            "code": self.code,
            "title": self.title,
            "content": self.content,
        }

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


class BaseStringReturn:
    def __init__(self, request, code, logging_description):
        self.request = request
        self.code = code
        self.logging_description = logging_description

    def __str__(self):
        username = "Anonymous"
        try:
            user = getattr(self.request, 'user', None)
            username = user.username if user and user.is_authenticated else "Anonymous"
        except Exception as e:
            username = "Anonymous"
        ip = self.get_client_ip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"[{timestamp}] - USER: {username} - IP: {ip} - {self.logging_description}"

    def get_client_ip(self):
        try:
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0]
            return self.request.META.get('REMOTE_ADDR', 'Unknown')
        except Exception:
            return "Unknown"


class BaseOnlyStringReturn:
    def __init__(self, code, logging_description):
        self.code = code
        self.logging_description = logging_description

    def __str__(self):
        username = "SYSTEM"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"[{timestamp}] - {username} - {self.logging_description}"
