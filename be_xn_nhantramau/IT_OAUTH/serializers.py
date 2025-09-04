# accounts/serializers.py
from rest_framework import serializers
# Ensure all necessary models are imported
from .models import User, Role, Application, AccessToken
# --- Existing Serializers (for context) ---
import json


class UserBaseShow(serializers.ModelSerializer):
    """
    Serializer for displaying basic, public-facing user information.
    Suitable for responses after login/registration or public profiles.
    """
    # Display role name instead of just ID
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'department_code', 'date_of_birth', 'gender', 'address',
            'role_name',  # The name of the role
            'active', 'date_joined', 'last_login',
            'created_date', 'updated_date'
        ]
        read_only_fields = fields  # All fields are read-only for this display serializer


class UserSerializer(serializers.ModelSerializer):
    """
    General serializer for the User model.
    Can be used for retrieving full user profiles (e.g., by admin or the user themselves).
    Includes all fields, with sensitive fields handled appropriately.
    """
    # Nested serializer for the Role, to show more details about the role
    # Or just display the name as in UserBaseShow
    role = serializers.StringRelatedField(
        read_only=True)  # Displays Role.__str__
    # Alternatively, if you want more role details:
    # role = RoleSerializer(read_only=True) # Requires RoleSerializer to be defined

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'department_code', 'date_of_birth', 'gender', 'address',
            'avatar',  # Include avatar field
            'role',  # The Role object or its string representation
            'is_staff', 'active', 'is_superuser',
            'date_joined', 'last_login',
            'created_date', 'updated_date'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'is_staff', 'active', 'is_superuser',
            'date_joined', 'last_login', 'created_date', 'updated_date', 'role'
        ]
        # You might add 'password' here with write_only=True if you want to allow
        # password changes via a general user update endpoint, but 'change_password'
        # action is usually preferred for security.

# --- NEW: Application Serializer ---


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Application model.
    Handles auto-generated client_id and client_secret as read-only.
    """
    class Meta:
        model = Application
        fields = [
            'id', 'name', 'description',
            'client_id', 'client_secret', 'active',
            'created_date', 'updated_date'
        ]
        read_only_fields = [
            'id', 'client_id', 'client_secret', 'active',
            'created_date', 'updated_date'
        ]
        # You can set extra_kwargs for fields like 'name' to be required
        extra_kwargs = {
            'name': {'required': True},
            'callback_url': {'required': True},
        }


# --- NEW Request Serializer ---
def serialize_request(request):
    META = None
    if hasattr(request, "META"):
        META = {key: request.META.get(key, None) for key in request.META}

    # Serialize as usual
    serialized_request = {
        "method": request.method,
        "path": request.path,
        "headers": {key: value for key, value in request.headers.items()},
        "META": META,
    }
    # Dump the serialized request as a JSON string
    string_json = json.dumps(serialized_request, indent=2, ensure_ascii=False)
    return string_json
