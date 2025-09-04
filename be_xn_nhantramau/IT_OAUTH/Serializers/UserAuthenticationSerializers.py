from rest_framework import serializers
# Ensure all necessary models are imported
from ..models import User, Role, Application, AccessToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

# Message
from general_utils.ResponseMessage import MESSAGE_INSTANCES


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={
                                     'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={
                                      'input_type': 'password'})

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password2', 'first_name', 'last_name',
            'phone_number', 'department_code', 'date_of_birth', 'gender', 'address'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    # === UPDATED: Make these fields optional for the superuser case ===
    client_id = serializers.UUIDField(write_only=True, required=False)
    client_secret = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        language = data.get('language')

        # --- 1. Authenticate the user ---
        user = authenticate(username=username, password=password)
        if user is None:
            # 'Tên người dùng hoặc mật khẩu không chính xác.'
            raise serializers.ValidationError(
                MESSAGE_INSTANCES("FAIL_OAUTH_DANG_NHAP_SAI_THONG_TIN_TK_MK", language), code='authorization')

        if not user.active:
            # 'Tài khoản người dùng đã bị khóa.'
            raise serializers.ValidationError(
                MESSAGE_INSTANCES("FAIL_OAUTH_THONG_TIN_TK_BI_KHOA", language), code='inactive')

        # --- 2. Conditional Application Authentication ---

        # Case A: User is a superuser
        if user.is_superuser:
            # If a superuser provides client credentials, validate them normally.
            if client_id and client_secret:
                try:
                    application = Application.objects.using(
                        'oauth').get(client_id=client_id, active=True)
                    if application.client_type == 'confidential' and application.client_secret != client_secret:
                        raise serializers.ValidationError(
                            MESSAGE_INSTANCES("FAIL_OAUTH_CONFIDENTIAL", language), code='invalid_client_secret')

                    data['application'] = application

                except ObjectDoesNotExist:
                    raise serializers.ValidationError(
                        MESSAGE_INSTANCES("FAIL_OAUTH_CONFIDENTIAL_NOT_EXISTED", language), code='client_not_found')

            # If a superuser does NOT provide client credentials, they are logging in for
            # administrative purposes, not on behalf of a specific app.
            # We set the application to None. The view will need to handle this.
            else:
                data['application'] = None

        # Case B: User is NOT a superuser
        else:
            # A standard user MUST provide valid client credentials.
            if not client_id or not client_secret:
                raise serializers.ValidationError(
                    MESSAGE_INSTANCES("FAIL_OAUTH_CONFIDENTIAL_REQUIRED_PROVIDE", language), code='missing_client_credentials')

            try:
                application = Application.objects.using(
                    'oauth').get(client_id=client_id, active=True)
                if application.client_type == 'confidential' and application.client_secret != client_secret:
                    raise serializers.ValidationError(
                        MESSAGE_INSTANCES("FAIL_OAUTH_CONFIDENTIAL_NOT_CORRECTED", language), code='invalid_client_secret')

                data['application'] = application

            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    MESSAGE_INSTANCES("FAIL_OAUTH_CONFIDENTIAL_NOT_EXSITED_OR_NOT_ACTIVED", language), code='client_not_found')

        # Attach the authenticated user to the validated data
        data['user'] = user
        return data


# --- NEW SERIALIZERS ---
