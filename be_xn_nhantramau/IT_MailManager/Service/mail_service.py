import json
import base64
from django.conf import settings
from django.template import Template, Context
from datetime import datetime


# Import redmail instead of Django's send_mail
from redmail import outlook

# Config
from IT_OAUTH.models import ConfigApp as ConfigAppOAuth

from IT_MailManager.models import FormMail, HistorySendMail
from IT_MailManager.Template.TemplateDataMail import SendEmailDataSetup

# general_utils imports
from general_utils.utils import create_temp_file, remove_temp_file
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelper
from general_utils.GetConfig.UtilsConfigSystem import (
    GET_VALUE_ACTION_SYSTEM,
    GET_VALUE_BASE64_ACTION_SYSTEM,
    CHECK_ACTION_SYSTEM,
    BOOL_CHECK_ACTION_SYSTEM,
)

logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")


def outlook_config_default():
    """
    Initializes the email service with Outlook configuration.
    This function should be called once at the start of your application.
    """
    try:
        OUTLOOK_SERVICE = outlook
        OUTLOOK_SERVICE.username = ""
        OUTLOOK_SERVICE.password = ""

        if GET_VALUE_ACTION_SYSTEM(
            ConfigAppOAuth, "USERNAME_SEND_MAIL_DEFAULT", dbname="oauth"
        ):
            OUTLOOK_SERVICE.username = GET_VALUE_ACTION_SYSTEM(
                ConfigAppOAuth, "USERNAME_SEND_MAIL_DEFAULT", dbname="oauth"
            )

        if GET_VALUE_BASE64_ACTION_SYSTEM(
            ConfigAppOAuth, "PASSWORD_SEND_MAIL_DEFAULT", dbname="oauth"
        ):
            OUTLOOK_SERVICE.password = GET_VALUE_BASE64_ACTION_SYSTEM(
                ConfigAppOAuth, "PASSWORD_SEND_MAIL_DEFAULT", dbname="oauth"
            )

        return OUTLOOK_SERVICE
    except Exception as e:
        print(f"Error initializing Outlook service: {str(e)}")
        return None


def send_form_mail(form_mail_name: str, context: dict, user=None):
    """
    Sends a FormMail template with dynamic data provided in the context using redmail.outlook.send.

    This is the full-option version of the function, which handles all data types including
    recipients, subject, HTML content, attachments, and embedded body images.

    :param form_mail_name: The name of the FormMail template to use (e.g., 'invoice_template').
    :param context: A dictionary containing all variables for the template, including 'recipients',
                    'subject', 'attachments', and 'body_images'.
    :param user: The User object who initiated the email, if applicable.
    :return: HistorySendMail object if successful, None otherwise.
    """
    try:
        # 1. Initialize the Outlook service
        outlook_service = outlook_config_default()
        if not outlook_service:
            return None

        # 2. Retrieve the FormMail template from the database
        form_mail = FormMail.objects.filter(
            name_form=form_mail_name, is_used=True, active=True
        ).first()

        if not form_mail:
            error_msg = (
                f"FormMail template '{form_mail_name}' not found or is not active."
            )
            HistorySendMail.objects.create(
                user=user,
                recipient_list=json.dumps(context.get(
                    "recipients", []), ensure_ascii=False),
                subject=context.get("subject", "N/A"),
                body=f"Failed to find template: {form_mail_name}",
                status="FAILED",
                error_message=error_msg,
            )
            return None

        # 3. Check for recipients before proceeding
        recipients = context.get("recipients", [])
        if not recipients:
            error_msg = "No recipients provided in the context."
            HistorySendMail.objects.create(
                user=user,
                recipient_list="[]",
                subject=context.get("subject", "No Subject"),
                body=form_mail.value,
                status="FAILED",
                error_message=error_msg,
            )
            return None

        # 4. Render the email subject and HTML content using the context
        subject_rendered = Template(context.get("subject", "No Subject")).render(
            Context(context)
        )
        html_content = Template(form_mail.value).render(Context(context))

        # 5. Populate the SendEmailDataSetup object with all dynamic content
        email_data = SendEmailDataSetup(
            subject=subject_rendered, html_content=html_content)
        email_data.add_recipients(recipients)

        list_temp_files = []
        # Add attachments and body images from the context
        for filename, value in context.get("attachments", {}).items():
            value_bytes = base64.b64decode(value)
            email_data.add_attachment(
                filename, value_bytes)
            # list_temp_files.append(temp_file)

        for cid, value in context.get("body_images", {}).items():
            temp_file = create_temp_file(
                # Added a file extension for clarity
                data=value, file_name=f"{cid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            email_data.add_body_image(cid, temp_file)
            list_temp_files.append(temp_file)

        # 6. Send the email using redmail.outlook
        status = "PENDING"
        error_message = None
        try:
            outlook_service.send(
                receivers=email_data.recipients,
                subject=email_data.subject,
                html=email_data.html_content,
                attachments=email_data.attachments,
                body_images=email_data.body_images,
            )
            status = "SENT"
        except Exception as e:
            status = "FAILED"
            error_message = str(e)

        # 7. Log the email sending history
        history_send = HistorySendMail.objects.create(
            user=user,
            recipient_list=json.dumps(
                email_data.recipients, ensure_ascii=False),
            subject=email_data.subject,
            body=email_data.html_content,
            status=status,
            error_message=error_message,
        )

        # 8. Clean up temporary files
        for temp_file in list_temp_files:
            remove_temp_file(temp_file)

        return history_send

    except Exception as e:
        error_msg = f"An unexpected error occurred in send_form_mail: {e}"
        return None


def test(test_image_path, test_attachment_path):
    import os
    from datetime import datetime

    # You'll need to create a dummy image and file for this test
    # A placeholder image for testing
    test_image_path = test_image_path or "/tmp/test_image.png"
    # A placeholder text file for testing
    test_attachment_path = test_attachment_path or "/tmp/test_attachment.txt"

    # Ensure the paths are absolute
    test_image_path = os.path.abspath(test_image_path)
    test_attachment_path = os.path.abspath(test_attachment_path)

    # Create dummy files for the test
    if not os.path.exists(test_image_path):
        # A simple way to create a blank file
        with open(test_image_path, "w") as f:
            f.write("")
    if not os.path.exists(test_attachment_path):
        with open(test_attachment_path, "w") as f:
            f.write("This is a test attachment.")

    # The context dictionary to pass to send_form_mail
    test_context = {
        # Required for sending
        "recipients": ["thuctran.2207@gmail.com", "thuctc@bth.org.vn"],
        "subject": "Thử nghiệm hệ thống gửi email: {{ test_id }}",
        # Template data (to fill placeholders)
        "company_name": "Công ty ABC",
        "full_name": "Người Dùng Thử Nghiệm",
        "dynamic_content": "Nội dung thử nghiệm thành công!",
        "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_id": "XYZ-123",
        # Attachments
        "attachments": {
            "test_document.txt": test_attachment_path,
        },
        # Embedded images
        "body_images": {
            "logo_img": test_image_path,
        },
    }
    return test_context
