import json
from IT_MailManager.models import FormMail

def save_form_mail(user, name_form, html_content, variables=None, type_form=None):
    """Saves or updates a FormMail instance."""
    form_mail, created = FormMail.objects.update_or_create(
        user=user,
        name_form=name_form,
        defaults={
            'value': html_content,
            'default_variables': json.dumps(variables or {}),
            'type_form': type_form,
            'is_used': True # Mark as used when saved
        }
    )
    return form_mail

def get_form_mail(name_form, user=None):
    """Retrieves a FormMail instance by name and optionally by user."""
    try:
        # Prioritize user-specific form, then a global one
        if user:
            return FormMail.objects.filter(name_form=name_form, user=user, is_used=True).first()
        return FormMail.objects.filter(name_form=name_form, is_used=True).first()
    except FormMail.DoesNotExist:
        return None

def render_form_mail(form_mail, context_data=None):
    """
    Substitutes variables into the HTML string.
    Context_data will override any default variables.
    """
    if not form_mail:
        return ""

    # Load default variables
    default_vars = json.loads(form_mail.default_variables)
    
    # Merge context data, giving it priority
    final_context = {**default_vars, **(context_data or {})}

    rendered_html = form_mail.value
    
    # Auto-target and replace variables in the HTML string
    for key, value in final_context.items():
        placeholder = f"{{{key}}}"
        rendered_html = rendered_html.replace(placeholder, str(value))
        
    return rendered_html