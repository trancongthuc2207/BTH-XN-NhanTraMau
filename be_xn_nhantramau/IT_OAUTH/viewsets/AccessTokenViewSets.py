# accounts/viewsets.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import login, logout  # Import login/logout functions
import logging

from IT_OAUTH.models import AccessToken, User  # Import User model
from IT_OAUTH.Serializers import UserAuthenticationSerializers
from IT_OAUTH.Serializers import AccessTokenSerializers

logger = logging.getLogger(__name__)

# --- AccessToken ViewSet (from previous step) ---


class AccessTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing and revoking user access tokens.
    Users can only see and revoke their own tokens.
    Admins can see all tokens and revoke any.
    """
    queryset = AccessToken.objects.all()
    serializer_class = AccessTokenSerializers.AccessTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return AccessToken.objects.all().select_related('user', 'application')
        return AccessToken.objects.filter(user=user, active=True).select_related('user', 'application')

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'revoke':
            return AccessTokenSerializers.AccessTokenDetailSerializer
        return AccessTokenSerializers.AccessTokenSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke(self, request, pk=None):
        """
        Custom action to revoke a specific access token.
        """
        try:
            # Enforce user ownership via get_queryset
            token = self.get_queryset().get(pk=pk)
        except AccessToken.DoesNotExist:
            return Response({'detail': 'Token not found or you do not have permission to access it.'},
                            status=status.HTTP_404_NOT_FOUND)

        if not token.active:
            return Response({'detail': 'Token is already revoked.'},
                            status=status.HTTP_400_BAD_REQUEST)

        token.revoke()
        logger.info(f"Token {pk} revoked by user {request.user.username}")

        return Response({'detail': 'Token successfully revoked.'}, status=status.HTTP_200_OK)


# --- User API ViewSet ---
class UserAuthViewSet(viewsets.ViewSet):
    """
    A ViewSet for user authentication actions: register, login, logout.
    """
    # Define permission classes for the entire ViewSet
    # Individual actions can override this
    # By default, allow anyone to access these endpoints
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        API endpoint for user registration.
        """
        serializer = UserAuthenticationSerializers.UserRegistrationSerializer(
            data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # You might want to automatically log in the user after registration
            # login(request, user) # If you want session-based login immediately
            return Response(
                {"message": "User registered successfully.",
                    "username": user.username, "email": user.email},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        API endpoint for user login.
        Authenticates user and establishes a session.
        """
        serializer = UserAuthenticationSerializers.UserLoginSerializer(
            data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)  # This establishes the Django session
            return Response(
                {"message": "Login successful.",
                    "username": user.username, "user_id": user.id},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        API endpoint for user logout.
        Invalidates the user's session.
        """
        if request.user.is_authenticated:
            logout(request)
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        return Response({"detail": "No active session to log out from."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        API endpoint to get details of the currently authenticated user.
        """
        # You might want a dedicated serializer for user profile data
        # For simplicity, returning basic info here
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "role": user.role.name if user.role else None,
            "phone_number": user.phone_number,
            "department_code": user.department_code,
            "date_of_birth": user.date_of_birth,
            "gender": user.gender,
            "address": user.address,
            "created_date": user.created_date,
            "updated_date": user.updated_date,
        }, status=status.HTTP_200_OK)
