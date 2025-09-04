# accounts/perms.py
from rest_framework import permissions
# from rest_framework.exceptions import PermissionDenied # You might want this for explicit errors


class IsAuthen(permissions.BasePermission):
    """
    Custom permission to check if the user is authenticated via custom logic
    (e.g., a token, which sets request.user).
    """

    def has_permission(self, request, view):
        # Check if request.user is set and is a valid user object.
        # This assumes your custom authentication middleware/class populates
        # request.user upon successful authentication.
        if hasattr(request, 'user') and request.user is not None and request.user.active:
            return True
        # If not authenticated, you might raise an exception directly
        # raise PermissionDenied("Authentication credentials were not provided or are invalid.")
        return False

    def has_object_permission(self, request, view, obj):
        # Implement object-level permissions if needed.
        # For now, it might just defer to has_permission or be more specific.
        return True  # Or implement specific logic if, for instance, a user can only edit their own profile
