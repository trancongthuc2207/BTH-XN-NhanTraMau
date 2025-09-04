from rest_framework import permissions
from django.conf import settings
from .models import *
from IT_OAUTH.models import Role


# -------- Action on User
# User do Authen
class IsAuthen:
    def has_permission(self, request, obj):
        match request.user:
            case None:
                return False
            case _:
                if request.user.is_superuser or request.user:
                    return True
                else:
                    return False


class RoleAppDefault:
    def has_permission(self, request, obj):
        match request.user:
            case None:
                return False
            case _:
                # if admin
                if request.user.is_superuser:
                    return True
                # if user active
                if request.user.active == False:
                    return False

                return False
