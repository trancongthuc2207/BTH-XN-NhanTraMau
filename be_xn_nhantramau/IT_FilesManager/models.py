from django.db import models
from IT_OAUTH.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.encoding import force_str
from django.conf import settings
import json
from datetime import datetime, timezone
import uuid
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import base64
import os
import mimetypes
from django.utils.translation import gettext_lazy as _


from general_utils.models import LogEntrySys, BaseModel as BaseModelGeneral, ConfigSystem, IPManager
# SOCKET_SYS
from IT_SOCKET_SYS.utils.NotifyUtils import send_sync_model_notification


def file_upload_path(instance, filename):
    """
    Constructs the dynamic upload path for the file, renaming the file to a UUID.
    Files will be organized within MEDIA_ROOT by the category's unique code.
    If no category is assigned, files go into an 'uncategorized' directory.
    Example: 'MEDIA_ROOT/uploaded_files/DOCS/a1b2c3d4-e5f6-7890-1234-567890abcdef.pdf'
    """
    category_folder = "uncategorized"
    if instance.category and instance.category.code:
        category_folder = instance.category.code.upper()  # Use uppercase for consistency

    # Get the file extension from the original filename
    ext = filename.split('.')[-1]
    # Generate a UUID for the new filename
    new_filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join('uploaded_files', category_folder, new_filename)


class LogEntryApp(LogEntrySys):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_log_file")

    class Meta:
        verbose_name_plural = "LOG HỆ THỐNG FILE"


class BaseModel(BaseModelGeneral):
    class Meta:
        abstract = True
        ordering = ['-created_date']

    def save(self, *args, **kwargs):
        if self.pk:  # If the instance already exists, compare changes
            old_instance = self.__class__.objects.filter(pk=self.pk).first()
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
                    "object_repr": force_str(self),
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


class Dictionary(BaseModel):
    """
    Model for storing key-value pairs for various configurations.
    Inherits from BaseModel to utilize common functionalities.
    """
    key = models.CharField(
        max_length=255,
        verbose_name=_("Key"),
        help_text=_("This dictionary entry.")
    )
    value = models.TextField(
        null=True,
        blank=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of this dictionary entry.")
    )
    type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Type"),
        help_text=_(
            "The type of this dictionary entry (e.g., 'config', 'setting').")
    )
    note = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Note"),
        help_text=_(
            "Any additional notes or comments about this dictionary entry.")
    )
    sort_index = models.SmallIntegerField(
        null=True,
        default=1,
        verbose_name=_("Sort Index"),
        help_text=_("Sort Index")
    )

    class Meta:
        verbose_name_plural = _('Dictionaries')
        ordering = ['key']  # Order entries alphabetically by key

    def __str__(self):
        return f"{self.key}: {self.value}"


class FileCategory(BaseModel):
    """
    Model for categorizing files.
    Inherits from BaseModel to utilize common functionalities.
    """
    name = models.CharField(
        max_length=1500,
        verbose_name=_("Category Name"),
        help_text=_(
            "A unique name for the file category (e.g., 'Documents', 'Images', 'Videos').")
    )
    # Added a 'code' field for unique, URL-friendly identification, ideal for folder names.
    code = models.CharField(
        max_length=50,
        verbose_name=_("Category Code"),
        help_text=_(
            "A unique, short code for the category (e.g., 'DOCS', 'IMG', 'VIDEOS'). Used for folder names.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of this file category.")
    )
    key_category = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Key Category"),
        help_text=_(
            "A unique key for the category, used for identification in APIs.")
    )
    category_child = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Category Child"),
        help_text=_("A list of child categories, if any, in JSON format.")
    )

    class Meta:
        verbose_name_plural = _('File Categories')
        ordering = ['name']  # Order categories alphabetically by name

    def __str__(self):
        # Using both name and code for clear identification
        return f"{self.name} ({self.code})"

    def check_existed_code_or_key_category_instance(file_category):
        existed_list = []
        try:
            # Get all active file categories with the same code or key_category
            existed_list = FileCategory.objects.using("default").filter(
                models.Q(code=file_category.code) | models.Q(
                    key_category=file_category.key_category),
                active=True
            )

            # If the instance has a primary key (i.e., it's being updated, not created),
            # filter itself out of the list of existed objects.
            if file_category.pk:
                existed_list = existed_list.exclude(pk=file_category.pk)

        except Exception as e:
            print(f"ERROR CHECK EXIST MODELS: {str(e)}")
            # You might want to re-raise the exception or handle it more gracefully
            # depending on your application's needs.

        return existed_list


class FileType(BaseModel):
    """
    Model for defining different types of files.
    Inherits from BaseModel to utilize common functionalities.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Type Name"),
        help_text=_(
            "A descriptive name for the file type (e.g., 'PDF Document', 'JPEG Image').")
    )
    extension = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("The file extension (e.g., 'pdf', 'docx', 'jpg')."),
        verbose_name=_("File Extension")
    )
    mimetype = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "The MIME type of the file (e.g., 'application/pdf', 'image/jpeg')."),
        verbose_name=_("MIME Type")
    )
    description = models.CharField(
        max_length=255,
        null=True,
    )

    class Meta:
        verbose_name_plural = _('File Types')
        ordering = ['name']  # Order file types alphabetically by name

    def __str__(self):
        if self.extension:
            return f"{self.name} (. {self.extension})"
        return self.name

    def check_existed_name_instance(file_type):
        existed_list = []
        try:
            # Get all active file categories with the same code or key_category
            existed_list = FileType.objects.using("default").filter(
                name__icontains=file_type.name,
                active=True
            )

            # If the instance has a primary key (i.e., it's being updated, not created),
            # filter itself out of the list of existed objects.
            if file_type.pk:
                existed_list = existed_list.exclude(pk=file_type.pk)

        except Exception as e:
            print(f"ERROR CHECK EXIST MODELS: {str(e)}")
            # You might want to re-raise the exception or handle it more gracefully
            # depending on your application's needs.

        return existed_list


# --- File Upload Path Callable ---
class Files(BaseModel):
    """
    Model for managing files in the system, including the actual file storage.
    Inherits from BaseModel for auditing features.
    """
    file_name = models.CharField(
        max_length=255,
        verbose_name=_("File Name"),
        help_text=_("The display name of the file.")
    )
    # FileField to store the actual file on the server.
    # 'upload_to' uses a callable function for dynamic path generation.
    # Django streams large files directly to disk, making this efficient for 25GB+ files.
    file = models.FileField(
        upload_to=file_upload_path, null=True, blank=True,
        verbose_name=_("File"),
        help_text=_("The actual file to be uploaded.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description or notes about the file.")
    )
    category = models.ForeignKey(
        FileCategory,
        on_delete=models.SET_NULL,  # If category is deleted, this field becomes NULL
        null=True,
        blank=True,
        related_name='files',
        verbose_name=_("Category"),
        help_text=_("The category this file belongs to.")
    )
    file_type = models.ForeignKey(
        FileType,
        on_delete=models.SET_NULL,  # If file type is deleted, this field becomes NULL
        null=True,
        blank=True,
        related_name='files',
        verbose_name=_("File Type"),
        help_text=_(
            "The type of this file (e.g., PDF, JPEG). Automatically detected if possible.")
    )
    file_size_bytes = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("File Size (bytes)"),
        help_text=_("Automatically populated with the file's size upon upload.")
    )
    checksum = models.CharField(
        max_length=64,  # Suitable for SHA-256 hash
        blank=True,
        null=True,
        verbose_name=_("Checksum (SHA256)"),
        help_text=_(
            "An optional cryptographic hash (SHA256) of the file content for integrity verification.")
    )
    password = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("password"),
        help_text=_("Password of files")
    )
    allowed_view = models.BooleanField(
        default=True,
        verbose_name=_("Allowed View"),
        help_text=_("Whether this file is allowed to be viewed by users.")
    )
    allowed_download = models.BooleanField(
        default=True,
        verbose_name=_("Allowed Download"),
        help_text=_("Whether this file is allowed to be downloaded by users.")
    )
    allơwed_edit = models.BooleanField(
        default=True,
        verbose_name=_("Allowed Edit"),
        help_text=_("Whether this file is allowed to be edited by users.")
    )
    required_authen = models.BooleanField(
        default=False,
        verbose_name=_("Required Authen"),
        help_text=_("User Required Authen")
    )
    # is_error dể check trạng thái file này đã cập nhật được file lên sau hay chưa
    is_error = models.BooleanField(
        default=False,
        verbose_name=_("Error"),
        help_text=_("User Required Authen")
    )
    # Trạng thái file
    status = models.SmallIntegerField(
        null=True,
        default=1,
        verbose_name=_("Status"),
        help_text=_("Status of file")
    )

    # Trạng thái file
    status = models.SmallIntegerField(
        null=True,
        default=1,
        verbose_name=_("Status"),
        help_text=_("Status of file")
    )

    # Code Index dùng để phân biệt cập nhật phiên bản
    code_index = models.CharField(
        null=True,
        max_length=256,
        verbose_name=_("code_index for Update version"),
        help_text=_(
            "A unique code_index for Update version")
    )
    # trường dùng để sắp xếp phiên bản
    sort_index = models.SmallIntegerField(
        null=True,
        default=1,
        verbose_name=_("Sort Index"),
        help_text=_("Sort Index")
    )

    class Meta:
        verbose_name_plural = _('Files')
        # Order files by creation date, newest first
        ordering = ['-created_date']

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically populate file_size_bytes and
        attempt to infer/set the file_type based on the uploaded file.
        This method might save the instance twice:
        1. Initial save by BaseModel (via super().save()) to place the file on disk.
        2. Second save (this method's conditional super().save()) to update
           file_size_bytes and file_type, which require the file to be on disk.
        """
        # Store initial state for comparison if this isn't the first save of this instance
        initial_file_name = self.file.name if self.file else None

        if not self.pk and not self.code_index:  # means it's a new instance
            self.code_index = GenerateCodeIndexFile()

        # Call the BaseModel's save method first. This handles logging of initial changes
        # and performs the actual file upload to storage via FileField.
        super().save(*args, **kwargs)

        # After the file has been potentially saved to storage by the FileField,
        # we can access its properties like size and name.
        updated_fields = []

        # Populate file_size_bytes if the file is present and size isn't set or has changed
        if self.file and self.file.name:
            if self.file_size_bytes is None or self.file_size_bytes != self.file.size:
                self.file_size_bytes = self.file.size
                updated_fields.append('file_size_bytes')

            # Try to infer file_type if it's not already set
            if not self.file_type:
                ext = os.path.splitext(self.file.name)[1].lstrip('.').lower()
                if ext:
                    try:
                        # Attempt to get an existing FileType or create a new one
                        file_type_obj, created = FileType.objects.get_or_create(
                            extension=ext,
                            defaults={'name': f"{ext.upper()} File"}
                        )
                        # If the mimetype for this FileType is not set, try to guess it
                        if not file_type_obj.mimetype:
                            guessed_mimetype, _ = mimetypes.guess_type(
                                self.file.name)
                            if guessed_mimetype:
                                file_type_obj.mimetype = guessed_mimetype
                                # Save the FileType instance
                                file_type_obj.save(update_fields=['mimetype'])

                        self.file_type = file_type_obj
                        updated_fields.append('file_type')
                    except Exception as e:
                        print(
                            f"Warning: Could not automatically set file type for '{self.file.name}'. Error: {e}")
            if self.file_type:
                ext = os.path.splitext(self.file.name)[1].lstrip('.').lower()
                if self.file_type.extension != ext:
                    try:
                        # Attempt to get an existing FileType or create a new one
                        file_type_obj, created = FileType.objects.get_or_create(
                            extension=ext,
                            defaults={'name': f"{ext.upper()} File"}
                        )
                        # If the mimetype for this FileType is not set, try to guess it
                        if not file_type_obj.mimetype:
                            guessed_mimetype, _ = mimetypes.guess_type(
                                self.file.name)
                            if guessed_mimetype:
                                file_type_obj.mimetype = guessed_mimetype
                                # Save the FileType instance
                                file_type_obj.save(update_fields=['mimetype'])

                        self.file_type = file_type_obj
                        updated_fields.append('file_type')
                    except Exception as e:
                        print(
                            f"Warning: Could not set diff file type for '{self.file.name}'. Error: {e}")

        # If any fields were updated in this second pass, save the model again.
        # Use update_fields to only save the changed fields and avoid re-uploading the file.
        if updated_fields:
            # Prevent infinite recursion by only updating the specific fields
            super().save(update_fields=updated_fields)


class FileInformation(BaseModel):
    """
    Model for storing additional information about files.
    Inherits from BaseModel to utilize common functionalities.
    """
    file = models.ForeignKey(
        Files,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("File"),
        help_text=_("The file this information is associated with.")
    )
    key = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("Key"),
        help_text=_("A unique key for this piece of information.")
    )
    value = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Value"),
        help_text=_("The value associated with the key.")
    )
    note = models.TextField(
        verbose_name=_("note"),
        null=True,
        blank=True,
    )
    type = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )

    class Meta:
        verbose_name_plural = _('File Information')

    def __str__(self):
        return f"{self.file.file_name} - {self.key}"


class IPManager(IPManager):
    class Meta:
        verbose_name_plural = "QUẢN LÝ IP"  # Plural name


class ConfigApp(ConfigSystem):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="user_config_file")

    class Meta:
        verbose_name_plural = "CÀI ĐẶT APP FILEMANAGER"


def GenerateCodeIndexFile():
    datetime_now = datetime.now()
    date_str = datetime_now.strftime("%Y%m%d")

    # Check how many codes exist for the current date
    num_is_available = (
        Files.objects.using("default")
        .filter(code_index=f"FILE/{date_str}")
        .count()
    )

    # Generate a unique code
    num_generate = num_is_available + 1  # Increment to ensure uniqueness
    code = f"FILE/{date_str}/{num_generate:05d}"  # Format with leading zeros

    # Check for uniqueness in the database
    while Files.objects.using("default").filter(code_index=code).exists():
        num_generate += 1
        code = f"FILE/{date_str}/{num_generate:05d}"

    return code
