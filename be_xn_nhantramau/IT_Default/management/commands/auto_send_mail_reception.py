from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import *
from ...utils.Utils import *


class Command(BaseCommand):
    help = "Send emails with merged participant information."

    # email :: hoten :: code_thanhvien :: code_hoinghi ;;
    def add_arguments(self, parser):
        parser.add_argument(
            "list_mail", type=str, help="List of mails separated by ';;'"
        )
        parser.add_argument("subject_mail", type=str, help="Subject of the email")

    def handle(self, *args, **options):
        list_mail = options["list_mail"]
        subject_mail = options["subject_mail"]

        list_success = []
        list_fail = []
        list_id_success = []
        list_id_fail = []
        list_convert = []

        try:
            # Get form mail template
            form_mail = (
                FormMail.objects.using("default")
                .filter(
                    id=GET_VALUE_ACTION_SYSTEM("SET_ID_FORM_RECEPTION"),
                    active=True,
                    is_used=True,
                )
                .first()
            )
            if not form_mail:
                raise CommandError("Form Mail không còn khả dụng!")

            if not subject_mail:
                raise CommandError("Thiếu tiêu đề mail!")

            # Process mail list
            mails = list_mail.split(";;")
            for mail in mails:
                if mail:
                    parts = mail.split("::")
                    if len(parts) != 4:
                        continue  # Skip invalid entries

                    (
                        mail_string,
                        hoten_string,
                        code_thanhvien_string,
                        code_hoinghi_string,
                    ) = parts

                    hoinghi = (
                        DM_HoiNghi.objects.using("default")
                        .filter(
                            code_hoinghi=code_hoinghi_string,
                            active=True,
                            is_current_used=DM_HoiNghi.CURRENT_USED,
                            is_expired=False,
                        )
                        .first()
                    )
                    if not hoinghi:
                        raise CommandError(
                            f"-{code_hoinghi_string}: Hội nghị không được khả dụng!"
                        )

                    list_convert.append(
                        {
                            f"{code_thanhvien_string}": {
                                "mail": mail_string,
                                "hoten": hoten_string,
                                "code_thanhvien": code_thanhvien_string,
                                "ten_hoinghis": f"[{hoinghi.name_hoinghi}]",
                            }
                        }
                    )

            # Merge duplicated participants
            merged = {}
            for entry in list_convert:
                for code, info in entry.items():
                    if code in merged:
                        if info["ten_hoinghis"] not in merged[code]["ten_hoinghis"]:
                            merged[code][
                                "ten_hoinghis"
                            ] += f" || {info['ten_hoinghis']}"
                    else:
                        merged[code] = info.copy()

            result = [{code: details} for code, details in merged.items()]

            # Sending merged emails
            outlook = settings.OUTLOOK_MAIL_RECEPTION
            for r in result:
                code, info = list(r.items())[0]
                content_form = form_mail.value.format(
                    hoten=info["hoten"],
                    my_image="""{{my_image}}""",
                    name_hoinghi=info["ten_hoinghis"],
                )

                try:
                    outlook.send(
                        receivers=[info["mail"]],
                        subject=subject_mail,
                        html=content_form,
                        attachments={},
                        body_images={},
                    )
                    list_success.append(code)
                    list_id_success.append(code)

                    # Update database record
                    thanhvien_upload = (
                        ThanhVienUpload.objects.using("default")
                        .filter(code_thanhvien=code)
                        .first()
                    )
                    if thanhvien_upload:
                        thanhvien_upload.is_send_mail = True
                        thanhvien_upload.save()

                except Exception as e:
                    list_fail.append(code)
                    list_id_fail.append(code)
                    self.stdout.write(
                        self.style.ERROR(f"Failed to send email to {info['mail']}: {e}")
                    )

            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success=",".join(list_id_success),
                list_fail=",".join(list_id_fail),
                totals=len(list_id_success),
            )
            history_send.save()

        except CommandError as e:
            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success=",".join(list_id_success),
                list_fail=",".join(list_id_fail),
                totals=len(list_id_success),
            )
            history_send.save()
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        except Exception as e:
            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success=",".join(list_id_success),
                list_fail=",".join(list_id_fail),
                totals=len(list_id_success),
            )
            history_send.save()
            self.stdout.write(self.style.ERROR(f"Unexpected Error: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Reception Mail: sending task completed."))
