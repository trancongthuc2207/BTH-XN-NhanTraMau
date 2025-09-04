# ten_ung_dung_cua_ban/admin.py

from django.contrib import admin
from django.apps import apps
from django.db.models import fields as model_fields, ForeignKey, DateTimeField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django import forms

# Get the current application configuration.
# REPLACE 'IT_MailManager' with your application name
current_app_config = apps.get_app_config('IT_MailManager')

# --- LIST OF MODELS AND FIELDS FOR SAFE HTML DISPLAY ---
# Use a dictionary to map a model name to a list of its fields
# that should be rendered as safe HTML in the admin list view.
SAFE_HTML_MODELS = {
    # Example: 'ModelName': ['field_one', 'field_two'],
    'FormMail': ['value']
}

# A list of models to exclude from automatic registration
EXCLUDE_MODELS = [
    'Session',
    'ContentType',
    'LogEntry',
    'Permission'
]


def create_optional_model_form(model):
    """
    Dynamically creates a ModelForm for the given model with all fields set to not required.
    This form will be used by the admin panel's change/add view.
    """
    class DynamicOptionalModelForm(forms.ModelForm):
        class Meta:
            model = model
            fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Loop through all fields and make them not required
            for field in self.fields:
                self.fields[field].required = False

    return DynamicOptionalModelForm


def create_safe_html_renderer(field_name):
    """
    Factory function to create a renderer function that displays
    HTML content safely without truncation.
    """
    @admin.display(description=field_name.capitalize().replace('_', ' '))
    def safe_html_renderer(self, obj):
        content = getattr(obj, field_name, '')
        # Use mark_safe to render the full HTML content without adding extra wrappers.
        return mark_safe(content)

    # Inform Django Admin that this content can contain HTML tags
    safe_html_renderer.allow_tags = True

    return safe_html_renderer


def create_model_admin(model):
    """
    This function dynamically creates a custom ModelAdmin class for a given model.
    It supports safe HTML display for specified fields.
    """

    list_display_fields = []
    search_fields = []
    list_filter_fields = []
    admin_class_attributes = {}

    # Get the list of safe HTML fields for the current model
    safe_html_fields = SAFE_HTML_MODELS.get(model.__name__, [])

    # Iterate through all fields in the model
    for field in model._meta.get_fields():
        field_name = field.name

        # Check if the field is a TextField and is in the list of safe HTML fields for this model
        if isinstance(field, model_fields.TextField) and field_name in safe_html_fields:
            # Use the factory function to create a safe renderer instance
            renderer_func = create_safe_html_renderer(field_name)

            # Add the method to the ModelAdmin class's attribute dictionary
            admin_class_attributes[renderer_func.__name__] = renderer_func
            list_display_fields.append(renderer_func.__name__)

        # Handle regular fields (including TextFields not declared as safe HTML)
        elif isinstance(field, (
            model_fields.CharField, model_fields.BooleanField,
            model_fields.IntegerField, model_fields.EmailField,
            ForeignKey, DateTimeField, model_fields.TextField
        )):
            list_display_fields.append(field_name)

        # Handle searchable fields
        if isinstance(field, (
            model_fields.CharField, model_fields.EmailField, model_fields.TextField
        )):
            search_fields.append(field_name)

        # Handle filterable fields
        if isinstance(field, (model_fields.BooleanField, ForeignKey, DateTimeField)):
            list_filter_fields.append(field_name)

    # Remove 'id' field from list_display if it exists
    if 'id' in list_display_fields:
        list_display_fields.remove('id')

    # Update the final attributes for the admin class
    admin_class_attributes['list_display'] = list_display_fields
    admin_class_attributes['search_fields'] = search_fields
    admin_class_attributes['list_filter'] = list_filter_fields

    # NEW: Link the dynamically created form to this ModelAdmin class
    admin_class_attributes['form'] = create_optional_model_form(model)

    # Important: Set the module name for correct Django recognition
    admin_class_attributes['__module__'] = 'django.contrib.admin'

    # Create a new class, inheriting from admin.ModelAdmin with the defined attributes
    return type(f"{model.__name__}Admin", (admin.ModelAdmin,), admin_class_attributes)


# Iterate through all models in the application
for model in current_app_config.get_models():
    # Skip models in the exclusion list
    if model.__name__ in EXCLUDE_MODELS:
        continue

    # Check if the model is already registered
    if not admin.site.is_registered(model):
        try:
            # Create a custom ModelAdmin class for this model
            model_admin = create_model_admin(model)
            # Register the model with the newly created Admin class
            admin.site.register(model, model_admin)
            print(f"✅ Registered model: {model.__name__} with full options.")
        except admin.sites.AlreadyRegistered:
            pass
        except Exception as e:
            print(f"❌ Error registering model {model.__name__}: {e}")
