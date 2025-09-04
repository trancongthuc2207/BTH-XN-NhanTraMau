
from django.utils.timezone import now
from ..models import *


# ---------------------------- #
# ---------------------------- #
# ---------- CHECK ----------- #
# ---------------------------- #
# ---------------------------- #

def BOOL_CHECK_ACTION_SYSTEM(action_name):
    # init response
    check = False
    try:
        config_action = (
            ConfigSystem.objects.using("oauth")
            .filter(name_config=action_name, status=True, active=True)
            .first()
        )
        if config_action:
            check = True

    except Exception as e:
        check = False
    return check


def GET_VALUE_ACTION_SYSTEM(action_name):
    # init response
    value = None
    try:
        config_action = (
            ConfigSystem.objects.using("oauth")
            .filter(name_config=action_name, status=True, active=True)
            .first()
        )
        if config_action:
            value = config_action.value

    except Exception as e:
        value = None
    return value
