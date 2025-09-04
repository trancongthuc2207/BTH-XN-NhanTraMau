from rest_framework import permissions
from django.conf import settings
from .models import *
from IT_OAUTH.models import RoleUser

# ----------- STATIC ROLE
# ALL_ROLE_BV = ["Admin_BV", 'NV_BV', 'LH_BV']
# ROLE_ADMIN_AND_NV_BV = ["Admin_BV", 'NV_BV']
ROLE_ADMIN = ['Admin_BV']


# -------- Action on User
# User do Authen
class IsAuthen():
    def has_permission(self, request, obj):
        match request.user:
            case None:
                return False
            case _:
                if request.user.is_superuser or request.user:
                    return True
                else:
                    return False

