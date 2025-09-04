# general_utils/logging_tools.py

import logging
from .logging_description import LoggingDescription, BaseStringReturn, BaseOnlyStringReturn


class LogHelper:
    def __init__(self, category):
        self.logger = logging.getLogger(category)

    def info(self, request, code, title, content):
        msg = BaseStringReturn(
            request, code, LoggingDescription(code, title, content))
        self.logger.info(msg)

    def warning(self, request, code, title, content):
        msg = BaseStringReturn(
            request, code, LoggingDescription(code, title, content))
        self.logger.warning(msg)


class LogHelperOnlyString:
    def __init__(self, category):
        self.logger = logging.getLogger(category)

    def info(self, code, title, content):
        msg = BaseOnlyStringReturn(
            code, LoggingDescription(code, title, content))
        self.logger.info(msg)

    def warning(self, code, title, content):
        msg = BaseOnlyStringReturn(
            code, LoggingDescription(code, title, content))
        self.logger.warning(msg)
