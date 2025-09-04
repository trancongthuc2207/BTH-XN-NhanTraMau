import logging
from .models import *

# Variable Save Logging
logger_sys_info = logging.getLogger('sys_info')
logger_sys_bug = logging.getLogger('sys_bug')

# ---------------------------- #
# ---------------------------- #
# ----------- USER ----------- #
# ---------------------------- #
# ---------------------------- #
# LOGIN
logger_user_login_info = logging.getLogger('log_user_login_info')
logger_user_login_bug = logging.getLogger('log_user_login_bug')
#
logger_user_info = logging.getLogger('log_user_info')
logger_user_bug = logging.getLogger('log_user_bug')

# ---------------------------- #
# ---------------------------- #
# ----------- ROOM ----------- #
# ---------------------------- #
# ---------------------------- #
logger_room_bug = logging.getLogger('log_room_bug')

code_info = {
    'success': 200,
    'bug': 300,
}


# CLASS INFO FOR LOGGING
class LoggingDescription:
    def __init__(self, code, title, content, status_write_msg):
        self.code_info = code
        self.title = title
        self.content = content
        self.status_write_msg = status_write_msg

    def __str__(self):
        return "\nCODE: {code}\nTITLE: {title}\nCONTENT: {content}\n".format(code=self.code_info,
                                                                             title=self.title,
                                                                             content=self.content)


def BaseStringReturn(request_input, status_code, logging_description):
    string_log_info = ""
    if logging_description.status_write_msg:
        string_log_info = "\"{user}\" {ip} \"{method} {url}\" {status_code} {logging_description}".format(
            user=request_input.user.username, ip=request_input.META.get("REMOTE_ADDR"),
            method=request_input.method,
            url=request_input.get_full_path(),
            status_code=status_code, logging_description=str(logging_description.__str__()))
    else:
        string_log_info = "\"{user}\" {ip} \"{method} {url}\" {status_code} ".format(user=request_input.user.username,
                                                                                     ip=request_input.META.get(
                                                                                         "REMOTE_ADDR"),
                                                                                     method=request_input.method,
                                                                                     url=request_input.get_full_path(),
                                                                                     status_code=status_code)
    return string_log_info


# ---------------------------- # # ---------------------------- #
# ---------------------------- # # ---------------------------- #
# ---------------------------- # # ---------------------------- #
# ---------------------------- # # ---------------------------- #
# ---------------------------- # # ---------------------------- #
# SYS
def SYS_ExcuteLoggingInfo(request_input, status_code, logging_description):
    return logger_sys_info.info(BaseStringReturn(request_input, status_code, logging_description))


def SYS_ExcuteLoggingBug(request_input, status_code, logging_description):
    return logger_sys_bug.warning(BaseStringReturn(request_input, status_code, logging_description))


# ---------------------------- #
# ---------------------------- #
# ----------- USER ----------- #
# ---------------------------- #
# ---------------------------- #
# UPDATE MY USER LOGGING
# LOGIN
def USER_ExcuteLogging_LOGIN_INFO(request_input, status_code, logging_description):
    return logger_user_login_info.info(BaseStringReturn(request_input, status_code, logging_description))


def USER_ExcuteLogging_LOGIN_BUG(request_input, status_code, logging_description):
    return logger_user_login_bug.warning(BaseStringReturn(request_input, status_code, logging_description))


#
def USER_ExcuteLogging_Info(request_input, status_code, logging_description):
    return logger_user_info.info(BaseStringReturn(request_input, status_code, logging_description))


#
def USER_ExcuteLogging_Bug(request_input, status_code, logging_description):
    return logger_user_bug.warning(BaseStringReturn(request_input, status_code, logging_description))


# ---------------------------- #
# ---------------------------- #
# ----------- ROOM ----------- #
# ---------------------------- #
# ---------------------------- #
def ROOM_ExcuteLogging_BUG(request_input, status_code, logging_description):
    return logger_room_bug.warning(BaseStringReturn(request_input, status_code, logging_description))
