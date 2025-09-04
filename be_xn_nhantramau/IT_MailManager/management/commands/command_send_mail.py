import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Assuming your send_form_mail function is located in a file like 'your_app/services/email_utils.py'
from IT_MailManager.Service.mail_service import send_form_mail

# general_utils imports
from general_utils.utils import split_and_clean


class Command(BaseCommand):
    help = "Send emails with a custom template and dynamic data using the send_form_mail utility."

    def add_arguments(self, parser):
        parser.add_argument(
            "form_mail_name",
            type=str,
            help="The name of the FormMail template to use (e.g., 'test_form_mail').",
        )
        parser.add_argument(
            "--context-json",
            type=str,
            help='Optional JSON string for extra context data (e.g., \'{"full_name":"John Doe"}\').',
            default="{}",
        )

    def handle(self, *args, **options):
        # 1. Parse command-line arguments and JSON context
        form_mail_name = options["form_mail_name"]
        # print(f"Context JSON: {options['context_json']}")

        try:
            extra_context = json.loads(options["context_json"])
        except json.JSONDecodeError:
            raise CommandError(
                "Invalid JSON provided for --context-json. Please check your syntax."
            )

        context_data = {
            **extra_context,  # Merge the extra context with the required data
        }

        self.stdout.write(
            f"Preparing to send '{context_data['subject']}' to {len(context_data['recipients'])} recipients using template '{form_mail_name}'..."
        )

        try:
            with transaction.atomic():
                # 3. Call the send_form_mail function
                # Note: We pass None for `request` and `user` as they don't exist in a management command.
                history_log = send_form_mail(
                    form_mail_name=form_mail_name,
                    context=context_data,
                    user=None,
                )

                # 4. Provide feedback to the user based on the result
                if history_log and history_log.status == "SENT":
                    self.stdout.write(
                        self.style.SUCCESS(f"Email successfully sent and logged.")
                    )
                else:
                    error_msg = (
                        history_log.error_message if history_log else "Unknown error"
                    )
                    self.stdout.write(
                        self.style.ERROR(f"Failed to send email. Error: {error_msg}")
                    )

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Command Error: {str(e)}"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An unexpected error occurred: {str(e)}")
            )

        self.stdout.write(self.style.SUCCESS("Mail sending task completed."))
