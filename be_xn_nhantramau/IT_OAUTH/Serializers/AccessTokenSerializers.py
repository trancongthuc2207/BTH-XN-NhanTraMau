from rest_framework import serializers
# Ensure all necessary models are imported
from ..models import User, Role, Application, AccessToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
# --- Existing Serializers (for context) ---


class AccessTokenSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(
        source='user.username', read_only=True)
    application_name = serializers.CharField(
        source='application.name', read_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = AccessToken
        fields = [
            'id', 'user_username', 'application_name', 'access_token',
            'refresh_token', 'expires_at', 'refresh_expires_at',
            'scope_list', 'active', 'created_date', 'updated_date'
        ]
        read_only_fields = fields


class AccessTokenDetailSerializer(AccessTokenSerializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta(AccessTokenSerializer.Meta):
        fields = AccessTokenSerializer.Meta.fields + \
            ['access_token', 'refresh_token']
        read_only_fields = fields


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        try:
            # Check if the refresh token exists and is active
            token_instance = AccessToken.objects.get(
                refresh_token=value,
                active=True,
                refresh_expires_at__gt=timezone.now()
            )
            return token_instance
        except AccessToken.DoesNotExist:
            raise serializers.ValidationError(
                "Mã làm mới không hợp lệ hoặc đã hết hạn.")
        except Exception:
            raise serializers.ValidationError(
                "Đã xảy ra lỗi khi xác thực mã làm mới.")
