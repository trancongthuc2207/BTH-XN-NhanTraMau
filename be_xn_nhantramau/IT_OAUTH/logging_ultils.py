import logging

# Logger registry
logger_sys_info = logging.getLogger('sys_info')
logger_sys_bug = logging.getLogger('sys_bug')

logger_user_login_info = logging.getLogger('log_user_login_info')
logger_user_login_bug = logging.getLogger('log_user_login_bug')
logger_user_info = logging.getLogger('log_user_info')
logger_user_bug = logging.getLogger('log_user_bug')

logger_room_bug = logging.getLogger('log_room_bug')

code_info = {
    'success': 200,
    'bug': 300,
}


# Class representing structured log content
class LoggingDescription:
    def __init__(self, code, title, content, status_write_msg=True):
        self.code_info = code
        self.title = title
        self.content = content
        self.status_write_msg = status_write_msg

    def __str__(self):
        return f"\nCODE: {self.code_info}\nTITLE: {self.title}\nCONTENT: {self.content}\n"


# Format the base log line with optional structured content
def BaseStringReturn(request_input, status_code, logging_description: LoggingDescription):
    username = getattr(request_input.user, 'username', 'Anonymous')
    ip = request_input.META.get("REMOTE_ADDR", "Unknown IP")
    method = request_input.method
    url = request_input.get_full_path()

    base = f'"{username}" {ip} "{method} {url}" {status_code}'

    if logging_description.status_write_msg:
        return f'{base} {str(logging_description)}'
    return base


# ---------------------------- #
# ----------- SYSTEM ----------#
# ---------------------------- #
def SYS_ExcuteLoggingInfo(request_input, status_code, logging_description):
    logger_sys_info.info(BaseStringReturn(
        request_input, status_code, logging_description))


def SYS_ExcuteLoggingBug(request_input, status_code, logging_description):
    logger_sys_bug.warning(BaseStringReturn(
        request_input, status_code, logging_description))


# ---------------------------- #
# ------------ USER -----------#
# ---------------------------- #
def USER_ExcuteLogging_LOGIN_INFO(request_input, status_code, logging_description):
    logger_user_login_info.info(BaseStringReturn(
        request_input, status_code, logging_description))


def USER_ExcuteLogging_LOGIN_BUG(request_input, status_code, logging_description):
    logger_user_login_bug.warning(BaseStringReturn(
        request_input, status_code, logging_description))


def USER_ExcuteLogging_Info(request_input, status_code, logging_description):
    logger_user_info.info(BaseStringReturn(
        request_input, status_code, logging_description))


def USER_ExcuteLogging_Bug(request_input, status_code, logging_description):
    logger_user_bug.warning(BaseStringReturn(
        request_input, status_code, logging_description))


# ---------------------------- #
# ------------ ROOM -----------#
# ---------------------------- #
def ROOM_ExcuteLogging_BUG(request_input, status_code, logging_description):
    logger_room_bug.warning(BaseStringReturn(
        request_input, status_code, logging_description))
