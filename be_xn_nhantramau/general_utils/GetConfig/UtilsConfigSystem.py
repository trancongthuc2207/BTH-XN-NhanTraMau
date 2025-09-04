from general_utils.models import *
from general_utils.Template.TemplateResponse import ResponseBase
from rest_framework.views import Response
from rest_framework import status
import base64


def CHECK_ACTION_SYSTEM(Instance, action_name, dbname="default"):
    # init response
    response = ResponseBase()
    try:
        config_action = (
            Instance.objects.using(dbname)
            .filter(name_config=action_name, status=True, is_used=True, active=True)
            .first()
        )
        if not config_action:
            response.set_data(None)
            response.set_message("Hành động này đang được khoá tạm thời!")
            response.set_status(response.STATUS_BAD_REQUEST)
            return Response(response.get(), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        response.set_data(None)
        response.set_message = str(e)
        response.set_status = response.STATUS_BAD_REQUEST
        return Response(response.get(), status=status.HTTP_400_BAD_REQUEST)
    return None


def BOOL_CHECK_ACTION_SYSTEM(Instance, action_name, dbname="default"):
    # init response
    check = False
    try:
        config_action = (
            Instance.objects.using(dbname)
            .filter(name_config=action_name, status=True, active=True)
            .first()
        )
        if config_action:
            check = True

    except Exception as e:
        check = False
    return check


def GET_VALUE_ACTION_SYSTEM(Instance, action_name, dbname="default"):
    # init response
    value = None
    try:
        config_action = (
            Instance.objects.using(dbname)
            .filter(name_config=action_name, status=True, active=True)
            .first()
        )
        if config_action:
            value = config_action.value

    except Exception as e:
        value = None
    return value


def GET_VALUE_BASE64_ACTION_SYSTEM(Instance, action_name, dbname="default"):
    # init response
    value = None
    try:
        config_action = (
            Instance.objects.using(dbname)
            .filter(name_config=action_name, status=True, active=True)
            .first()
        )
        if config_action:
            # Corrected line: b64decode returns bytes, then decode to string
            value = base64.b64decode(config_action.value).decode("utf-8")

    except Exception as e:
        print(f"Error decoding base64 value for {action_name}: {str(e)}")
        value = None

    return value
