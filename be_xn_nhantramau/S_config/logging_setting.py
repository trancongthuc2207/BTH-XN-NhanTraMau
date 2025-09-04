import atexit
import os
import logging
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler


# ✅ Custom handler with delay and auto-folder creation
class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, base_path, base_name, when='midnight', interval=1, backupCount=30, encoding='utf-8'):
        os.makedirs(base_path, exist_ok=True)
        filename = os.path.join(base_path, f"{base_name}.log")
        super().__init__(
            filename, when=when, interval=interval,
            backupCount=backupCount, encoding=encoding, delay=True  # ✅ Delay open
        )
        self.suffix = "%Y-%m-%d"

# ✅ Close loggers on shutdown


def close_all_loggers():
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.flush()
            handler.close()
        logger.handlers.clear()


atexit.register(close_all_loggers)

# ✅ Logging config
Setting = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "main_formatter": {
            "format": "{asctime} - {levelname} - {module} - {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "main_formatter",
        },
        # SYSTEM LOGS
        'file_info_sys': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Info/Sys',
            'base_name': 'sys-info',
            'formatter': 'main_formatter',
            'level': "INFO",
        },
        'file_bug_sys': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Bug/Sys',
            'base_name': 'sys-bug',
            'formatter': 'main_formatter',
            'level': "WARNING",
        },

        # USER LOGS
        'log_user_login_info': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Info/User',
            'base_name': 'login',
            'formatter': 'main_formatter',
            'level': "INFO",
        },
        'log_user_login_bug': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Bug/User',
            'base_name': 'login',
            'formatter': 'main_formatter',
            'level': "WARNING",
        },
        # --
        'log_user_info': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Info/User',
            'base_name': 'info',
            'formatter': 'main_formatter',
            'level': "INFO",
        },
        'log_user_bug': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Bug/User',
            'base_name': 'bug',
            'formatter': 'main_formatter',
            'level': "WARNING",
        },

        # THÀNH VIÊN LOG
        'log_thanhvien_upload_info': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Info/ThanhVienUpload',
            'base_name': 'thanhvien_upload_info',
            'formatter': 'main_formatter',
            'level': "INFO",
        },
        'log_thanhvien_upload_bug': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Bug/ThanhVienUpload',
            'base_name': 'thanhvien_upload_bug',
            'formatter': 'main_formatter',
            'level': "WARNING",
        },

        # REQUEST PAYMENT LOG
        'log_payment_request_bug': {
            '()': CustomTimedRotatingFileHandler,
            'base_path': 'loggs/Bug/PaymentRequest',
            'base_name': 'payment_request_bug',
            'formatter': 'main_formatter',
            'level': "WARNING",
        },

        # Just showing one example for clarity
        # REQUEST LOGS
        "log_request": {
            "()": CustomTimedRotatingFileHandler,
            "base_path": "loggs/Request",
            "base_name": "request_log",
            "formatter": "main_formatter",
            "level": "INFO",
        },

        # SOCKET LOGS
        "log_socket_bug": {
            "()": CustomTimedRotatingFileHandler,
            "base_path": "loggs/Bug/Socket",
            "base_name": "socket_bug",
            "formatter": "main_formatter",
            "level": "WARNING",
        },

        # MAIL LOGS
        "log_mail_bug": {
            "()": CustomTimedRotatingFileHandler,
            "base_path": "loggs/Bug/Mail",
            "base_name": "mail_bug",
            "formatter": "main_formatter",
            "level": "WARNING",
        },
    },
    "loggers": {
        # SYSTEM LOGS
        "file_info_sys": {
            "handlers": ["file_info_sys"],
            "propagate": False,
            "level": "INFO",
        },
        "file_bug_sys": {
            "handlers": ["file_bug_sys"],
            "propagate": False,
            "level": "WARNING",
        },
        # USER LOGS
        "log_user_login_info": {
            "handlers": ["log_user_login_info"],
            "propagate": False,
            "level": "INFO",
        },
        "log_user_login_bug": {
            "handlers": ["log_user_login_bug"],
            "propagate": False,
            "level": "WARNING",
        },
        "log_user_info": {
            "handlers": ["log_user_info"],
            "propagate": False,
            "level": "INFO",
        },
        "log_user_bug": {
            "handlers": ["log_user_bug"],
            "propagate": False,
            "level": "WARNING",
        },
        # THÀNH VIÊN LOG
        "log_thanhvien_upload_info": {
            "handlers": ["log_thanhvien_upload_info"],
            "propagate": False,
            "level": "INFO",
        },
        "log_thanhvien_upload_bug": {
            "handlers": ["log_thanhvien_upload_bug"],
            "propagate": False,
            "level": "WARNING",
        },
        # REQUEST PAYMENT LOG
        "log_payment_request_bug": {
            "handlers": ["log_payment_request_bug"],
            "propagate": False,
            "level": "WARNING",
        },
        # REQUEST LOGS
        "log_request": {
            "handlers": ["log_request"],
            "propagate": True,
            "level": "INFO",
        },
        # SOCKET LOGS
        "log_socket_bug": {
            "handlers": ["log_socket_bug"],
            "propagate": False,
            "level": "WARNING",
        },
        # MAIL LOGS
        "log_mail_bug": {
            "handlers": ["log_mail_bug"],
            "propagate": False,
            "level": "WARNING",
        },
    },
}

# ✅ Apply config
dictConfig(Setting)
