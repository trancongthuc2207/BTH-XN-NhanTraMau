from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import *
from ...utils.Utils import *
from general_utils.utils import split_and_clean


class Command(BaseCommand):
    help = "Send emails OTP"

    # email :: id_tv_upload :: hoten :: link :: image ;;
    def add_arguments(self, parser):
        # hoten:: ;;
        parser.add_argument("subject_mail", type=str, help="Tên tiêu đề mail otp")
        parser.add_argument("email", type=str, help="Email để gửi'")
        parser.add_argument(
            "list_number", type=str, help="Dãy số otp, gồm 4 số, ngăn cách bằng ';;'"
        )
        parser.add_argument("second_expired", type=str, help="Số giây hết hạn")

    def handle(self, *args, **options):
        subject_mail = options["subject_mail"]
        list_number = split_and_clean(options["list_number"])
        email = options["email"]
        second_expired = options["second_expired"]
        try:
            # Get form mail template
            form_mail = (
                FormMail.objects.using("default")
                .filter(
                    id=GET_VALUE_ACTION_SYSTEM("SET_ID_FORM_OTP_CUSTOM"),
                    active=True,
                    is_used=True,
                )
                .first()
            )
            if not form_mail:
                raise CommandError("Form Mail không còn khả dụng!")

            if not subject_mail:
                raise CommandError("Thiếu tiêu đề mail!")

            # Sending merged emails
            outlook = settings.OUTLOOK_MAIL_RECEPTION

            content_form = form_mail.value.format(
                number_1=list_number[0],
                number_2=list_number[1],
                number_3=list_number[2],
                number_4=list_number[3],
            )
            try:
                outlook.send(
                    receivers=[email],
                    subject=subject_mail,
                    html=content_form,
                    attachments={},
                    body_images={},
                )
                # Save email history
                history_send = HistorySendMail(
                    user=None,
                    name_form=form_mail.name_form,
                    list_success=email,
                    list_fail="",
                    totals=1,
                )
                history_send.save()

            except Exception as e:
                # Save email history
                history_send = HistorySendMail(
                    user=None,
                    name_form=form_mail.name_form,
                    list_success="",
                    list_fail=email,
                    totals=1,
                )
                history_send.save()
                self.stdout.write(self.style.ERROR(f"Failed: {e}"))

        except CommandError as e:
            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success="",
                list_fail=email,
                totals=1,
            )
            history_send.save()
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        except Exception as e:
            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success="",
                list_fail=email,
                totals=1,
            )
            history_send.save()
            self.stdout.write(self.style.ERROR(f"Unexpected Error: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Mail sending task completed."))
