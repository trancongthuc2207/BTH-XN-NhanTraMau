import secrets  # For generating secure random strings
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_str
from django.contrib.admin.models import CHANGE
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import uuid  # Import for UUID field
import os
import json

#
from general_utils.models import LogEntrySys, BaseModel as BaseModelGeneral, ConfigSystem, IPManager
# SOCKET_SYS
from IT_SOCKET_SYS.utils.NotifyUtils import send_sync_model_notification
# Helper function for user avatar path


def user_avatar_path(instance, filename):
    """
    Generates upload path for user avatars.
    file will be uploaded to MEDIA_ROOT/user_avatars/<username>/<filename>
    """
    # Ensure username is slugified or cleaned to be a valid path component
    username_slug = instance.username.replace('.', '_').replace('@', '_')
    return os.path.join('user_avatars', username_slug, filename)


class LogEntryApp(LogEntrySys):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_log_oauth")

    class Meta:
        verbose_name_plural = "LOG HỆ THỐNG OAUTH"


class BaseModel(BaseModelGeneral):
    class Meta:
        abstract = True
        ordering = ['-created_date']

    def save(self, *args, **kwargs):
        if self.pk:  # If the instance already exists, compare changes
            old_instance = self.__class__.objects.filter(pk=self.pk).first()
            LIST_CHANGE_FIELD = []
            if old_instance:
                changed_fields = {}
                for field in self._meta.fields:
                    old_value = getattr(old_instance, field.name)
                    new_value = getattr(self, field.name)

                    # If the field is a foreign key, compare by ID
                    if isinstance(field, models.ForeignKey):
                        old_value = old_value.pk if old_value else None
                        new_value = new_value.pk if new_value else None

                    # If the old or new value is a datetime, convert it to string
                    if isinstance(old_value, datetime):
                        old_value = old_value.strftime("%Y-%m-%d %H:%M:%S.%f")
                    if isinstance(new_value, datetime):
                        new_value = new_value.strftime("%Y-%m-%d %H:%M:%S.%f")

                    # Handle ImageField and FileField
                    if isinstance(field, models.ImageField) or isinstance(
                        field, models.FileField
                    ):
                        old_value = old_value.name if old_value else None
                        new_value = new_value.name if new_value else None

                    # 🔹 Fix: Handle float precision issues
                    if isinstance(old_value, float) or isinstance(old_value, Decimal):
                        # Convert to string with 6 decimal places
                        old_value = f"{old_value:.6f}"
                    if isinstance(new_value, float) or isinstance(new_value, Decimal):
                        new_value = f"{new_value:.6f}"

                    if old_value != new_value:
                        changed_fields[field.name] = {
                            "old": old_value,
                            "new": new_value,
                        }
                        LIST_CHANGE_FIELD.append(field.name)

                # if changed_fields and self.modified_by:
                if changed_fields:
                    change_message = json.dumps(
                        [{"changed": changed_fields}], ensure_ascii=False)
                    self.log_action(self.modified_by, CHANGE, change_message)

            # Notify Channel Layer if the model has a channel layer
            send_sync_model_notification(
                model_name=self.__class__.__name__,
                item_id=str(self.pk),
                payload={
                    "action": "log_action",
                    "model_name": self.__class__.__name__,
                    "event": "update",
                    "object_id": str(self.pk),
                    "object_repr": force_str(self, encoding="utf-8", strings_only=False, errors="strict"),
                })
            if "last_login" in LIST_CHANGE_FIELD and self.__class__.__name__ in ["User"]:
                send_sync_model_notification(
                    model_name=self.__class__.__name__,
                    item_id=str(self.pk),
                    payload={
                        "action": "login_action",
                        "model_name": self.__class__.__name__,
                        "event": "login",
                        "object_id": str(self.pk),
                        "object_repr": force_str(self, encoding="utf-8", strings_only=False, errors="strict"),
                    })
        else:
            # Optionally log creation (ADDITION) here if needed
            pass
        super().save(*args, **kwargs)

    def log_action(self, user, action_flag, change_message):
        LogEntryApp.objects.create(
            user=user,
            content_type_name=self.__class__.__name__,
            object_id=self.pk,
            object_repr=force_str(self),
            action_flag=action_flag,
            change_message=change_message,
            ip_address=self._ip_address,
            session_key=self._session_key,
        )


class Application(BaseModel):
    """
    Represents an OAuth client application.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique name of the client application."
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed description of the application."
    )

    # OAuth Client ID and Secret
    client_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for the client application (Public)."
    )
    client_secret = models.CharField(
        # A good length for securely generated secrets (e.g., SHA256 hash)
        max_length=128,
        unique=True,
        editable=False,  # Should not be directly editable in admin
        help_text="Secret key for the client application (Confidential). Should be securely generated."
    )

    # OAuth Callback/Redirect URIs
    # For multiple URIs, you might use a ManyToMany field to a separate model,
    # or store as a JSONField, or a comma-separated string.
    # A simple approach for one or a few:
    redirect_uris = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated list of allowed redirect URIs for authorization flow."
    )

    # Client type (e.g., 'confidential', 'public')
    CLIENT_TYPE_CHOICES = [
        ('confidential', 'Confidential (Requires client secret)'),
        ('public', 'Public (e.g., mobile apps, browser-based apps - no secret)'),
    ]
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='confidential',
        help_text="Type of the client application (confidential or public)."
    )

    # Owner of the application (e.g., who registered it)
    owner = models.ForeignKey(
        'User',  # Reference your custom User model if it's not directly 'auth.User'
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_applications",
        help_text="The user who registered or owns this application."
    )

    class Meta:
        verbose_name = "OAuth Client Application"
        verbose_name_plural = "OAuth Client Applications"
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.client_secret:
            # Generate a secure client secret only when creating the instance
            # In a real app, use a proper cryptographic hash function.
            import hashlib
            import os
            self.client_secret = hashlib.sha256(os.urandom(60)).hexdigest()
        super().save(*args, **kwargs)


class Scope(BaseModel):
    """
    Defines a specific permission scope for OAuth authorization.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for the scope (e.g., 'read_profile', 'write_data')."
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Human-readable description of what this scope grants access to."
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If true, this scope is implicitly granted if no scopes are requested."
    )

    class Meta:
        verbose_name = "OAuth Scope"
        verbose_name_plural = "OAuth Scopes"
        ordering = ['name']

    def __str__(self):
        return self.name


class AuthorizationCode(BaseModel):
    """
    Stores authorization codes issued to clients during the OAuth 2.0 authorization flow.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="auth_codes",
        help_text="The user who authorized this code."
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="auth_codes",
        help_text="The client application to which this code was issued."
    )
    code = models.CharField(
        max_length=128,  # Sufficient length for a securely generated code
        unique=True,
        help_text="The actual authorization code string."
    )
    redirect_uri = models.URLField(
        max_length=500,
        help_text="The redirect URI used during the authorization request."
    )
    expires_at = models.DateTimeField(
        help_text="Timestamp when this authorization code expires."
    )
    is_redeemed = models.BooleanField(
        default=False,
        help_text="Indicates if this code has already been exchanged for an access token."
    )

    # Store the scopes granted with this code (e.g., as a comma-separated string)
    # A ManyToManyField to Scope would be more robust for complex permission sets.
    # For simplicity, let's use a TextField here.
    scope_list = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated list of scopes granted with this authorization code."
    )

    class Meta:
        verbose_name = "OAuth Authorization Code"
        verbose_name_plural = "OAuth Authorization Codes"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['user', 'application']),
        ]

    def __str__(self):
        return f"Code for {self.user.username} to {self.application.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a secure random code
            # Generates a URL-safe text string
            self.code = secrets.token_urlsafe(64)
        if not self.expires_at:
            # Set a default expiration, e.g., 5 minutes from now
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)


class AccessToken(BaseModel):
    """
    Stores OAuth 2.0 access and refresh tokens.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="tokens",  # Renamed from 'access_tokens' for clarity
        help_text="The user who granted access."
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        related_name="tokens",
        null=True,   # <-- Add this
        blank=True,  # <-- Add this
        help_text="The client application for which the token was issued. Can be null for admin tokens."
    )

    access_token = models.CharField(
        max_length=512,  # Increased length slightly for longer JWTs
        unique=True,
        help_text="The actual access token string."
    )
    refresh_token = models.CharField(
        max_length=512,
        unique=True,
        null=True,  # Refresh token is optional for some flows
        blank=True,
        help_text="The refresh token string, if issued."
    )

    expires_at = models.DateTimeField(
        help_text="Timestamp when the access token expires."
    )
    refresh_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the refresh token expires."
    )

    # Store the scopes granted to this token
    # Again, ManyToManyField to Scope is ideal, but TextField for simplicity
    scope_list = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated list of scopes granted to this token."
    )

    class Meta:
        verbose_name = "OAuth Access Token"
        verbose_name_plural = "OAuth Access Tokens"
        indexes = [
            models.Index(fields=['access_token']),
            models.Index(fields=['refresh_token']),
        ]

    def __str__(self):
        return f"Access Token for {self.user.username} to {self.application.name} (Active: {self.active})"

    def revoke(self):
        """Revokes both access and refresh tokens."""
        self.active = False
        self.save()

    def is_expired(self):
        """Checks if the access token has expired."""
        return self.expires_at < timezone.now()

    def is_refresh_expired(self):
        """Checks if the refresh token has expired."""
        return self.refresh_expires_at and self.refresh_expires_at < timezone.now()

    def is_valid(self):
        """Checks if the access token is active and not expired."""
        return self.active and not self.is_expired()

    # === NEW: Add this save method ===
    def save(self, *args, **kwargs):
        if not self.access_token:
            # Generate a secure, URL-safe random string for the access token
            self.access_token = secrets.token_urlsafe(
                64)  # 64 bytes for a good length

        if self.refresh_token is None and self.application and self.application.client_type == 'confidential':
            # Generate a refresh token only if it's a confidential client and not already set
            self.refresh_token = secrets.token_urlsafe(64)

        super().save(*args, **kwargs)
    # === END NEW save method ===

# --- ROLE MODEL (Re-confirmed for context, previously RoleUser) ---


class Role(BaseModel):
    """
    Represents a user role in the system.
    """
    role_code = models.CharField(
        max_length=100,
        unique=True,
        help_text="A unique code for the role (e.g., 'admin', 'standard_user')"
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Human-readable name of the role (e.g., 'Administrator')"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="A brief description of the role's permissions or purpose"
    )

    def __str__(self):
        return self.name


class Department(BaseModel):
    """
    A model to store department codes and their corresponding names.
    """
    code = models.CharField(max_length=150, null=True, blank=True, unique=True)
    name = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


# --- TÀI KHOẢN NGƯỜI DÙNG (USER ACCOUNT) ---
class User(AbstractUser, BaseModel):
    """
    Custom user model extending Django's AbstractUser.
    Includes additional profile information and links to a Role.
    """
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,  # Can be null in the database
        blank=True,  # Can be left blank in forms
        help_text="Profile picture of the user."
    )
    phone_number = models.CharField(
        # Increased max_length for international numbers (original was 12)
        max_length=15,
        blank=True,  # Can be left blank in forms
        default="",  # Default to empty string instead of NULL for CharField
        help_text="User's phone number."
    )
    # Renamed 'ma_kp' to a more descriptive 'employee_id' or 'department_code'
    # Assuming 'ma_kp' stands for 'mã kết quả' or 'mã khoa phòng' (department code)
    department_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Internal department or specific code for the user."
    )

    # Changed from DateTimeField to DateField if only the date is needed
    # If time is truly relevant (e.g., exact birth time), keep DateTimeField.
    date_of_birth = models.DateField(
        null=True,  # Can be null in the database
        blank=True,  # Can be left blank in forms
        help_text="User's date of birth."
    )
    gender = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="User's gender (e.g., 'Male', 'Female', 'Other')."
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="User's physical address."
    )

    # Role relationship
    # Link to the optimized 'Role' model (formerly 'RoleUser')
    role = models.ForeignKey(
        Role,
        # If a role is deleted, users with that role will have role=NULL
        on_delete=models.SET_NULL,
        null=True,  # Allows the role to be null in the database
        blank=True,  # Allows the role field to be empty in forms
        related_name="users",  # Allows reverse access: role.users.all()
        help_text="The role assigned to the user."
    )

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
        # Add indexes for fields you frequently filter or order by
        indexes = [
            models.Index(fields=['username']),
            # If email is often used for lookup
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            # If you frequently filter users by role
            models.Index(fields=['role']),
        ]

    def set_avatar(self, file):
        """
        Sets the user's avatar file and saves the instance.
        """
        self.avatar = file
        self.save()

    def __str__(self):
        # Provide a more informative string representation
        # Use full name if available, otherwise fallback to username
        return self.get_full_name() or self.username


class ConfigApp(ConfigSystem):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_config_oauth")

    class Meta:
        verbose_name_plural = "CÀI ĐẶT APP OAUTH"


class IPManager(IPManager):
    ERROR_SPAM = 429

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_ip_oauth")

    class Meta:
        verbose_name_plural = "QUẢN LÝ IP"  # Plural name


class ResponseLog(BaseModel):
    """
    Model để ghi lại nhật ký các phản hồi API hoặc truy cập file.
    """
    # Trạng thái HTTP của phản hồi, ví dụ: 200, 404, 500
    status_code = models.PositiveSmallIntegerField(
        help_text="HTTP status code of the response."
    )

    # URL mà người dùng đã truy cập
    path = models.CharField(
        max_length=255,
        help_text="The URL path that was requested."
    )

    # Thông tin về người dùng đã thực hiện request (nếu có)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Không xóa log nếu user bị xóa
        null=True,
        blank=True,
        help_text="The user who made the request."
    )

    # Thời gian phản hồi được gửi đi
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time the response was sent."
    )

    # Phương thức của request, ví dụ: GET, POST
    method = models.CharField(
        max_length=10,
        help_text="The HTTP method of the request."
    )

    # Kích thước phản hồi (tính bằng byte)
    response_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The size of the response in bytes."
    )

    # Lưu lại địa chỉ IP của người dùng
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="The IP address of the user."
    )

    # Mô tả thêm về phản hồi, ví dụ: "File viewed", "API success"
    message = models.CharField(
        max_length=255,
        blank=True,
        help_text="A short message describing the response."
    )

    # Thêm trường để lưu nội dung phản hồi
    content = models.TextField(
        null=True,
        blank=True,
        help_text="The content of the response."
    )

    class Meta:
        verbose_name = "Response Log"
        verbose_name_plural = "Response Logs"
        ordering = ['-timestamp']  # Sắp xếp theo thời gian mới nhất trước

    def __str__(self):
        # Trả về chuỗi đại diện dễ đọc
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.status_code} {self.method} {self.path}"
