from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import *
from ...utils.Utils import *
from general_utils.utils import split_and_clean


class Command(BaseCommand):
    help = "Send send documents to members in one event"

    # email :: id_tv_upload :: hoten :: link :: image ;;
    def add_arguments(self, parser):
        # hoten:: ;;
        parser.add_argument("subject_mail", type=str,
                            help="Tên tiêu đề mail gửi tài liệu")
        parser.add_argument("code_hoinghi", type=str, help="Code hội nghị")
        parser.add_argument(
            "list_content", type=str, help="Nội dung ';;;'"
        )

    def handle(self, *args, **options):
        subject_mail = options["subject_mail"]
        code_hoinghi = options["code_hoinghi"]
        list_content = split_and_clean(options["list_content"], ';;;')
        list_success = []
        list_fail = []
        try:
            # Get form mail template
            form_mail = (
                FormMail.objects.using("default")
                .filter(
                    id=GET_VALUE_ACTION_SYSTEM(
                        "SET_ID_FORM_SEND_DOCUMENT_AND_LINK"),
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
                noi_dung=list_content[0],
                noi_dung_1=list_content[1],
            )

            # get danh sách mail
            list_email = []
            list_tv_main = HoiNghiThanhVien.objects.using(
                "default").filter(code_hoinghi=code_hoinghi, active=True)
            for tv in list_tv_main:
                if tv.email:
                    list_email.append(tv.email)

            hoinghi = (
                DM_HoiNghi.objects.using("default")
                .filter(
                    code_hoinghi=code_hoinghi,
                    active=True,
                )
                .first()
            )
            if hoinghi:
                if hoinghi.code_hn_include:
                    list_code_hn_include = split_and_clean(
                        hoinghi.code_hn_include)
                    for code in list_code_hn_include:
                        list_tv_include = HoiNghiThanhVien.objects.using(
                            "default").filter(code_hoinghi=code, active=True)
                        for tv in list_tv_include:
                            if tv.email:
                                list_email.append(tv.email)

            try:
                for email_ in list_email:
                    outlook.send(
                        receivers=[email_],
                        subject=subject_mail,
                        html=content_form,
                        attachments={},
                        body_images={},
                    )
                    list_success.append(email_)

                # Save email history
                history_send = HistorySendMail(
                    user=None,
                    name_form=form_mail.name_form,
                    list_success=",".join(list_success),
                    list_fail=",".join(list_fail),
                    totals=1,
                )
                history_send.save()

            except Exception as e:
                # Save email history
                history_send = HistorySendMail(
                    user=None,
                    name_form=form_mail.name_form,
                    list_success=",".join(list_success),
                    list_fail=",".join(list_fail),
                    totals=len(list_success),
                )
                history_send.save()
                self.stdout.write(self.style.ERROR(f"Failed: {e}"))

        except CommandError as e:
            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success=",".join(list_success),
                list_fail=",".join(list_fail),
                totals=len(list_success),
            )
            history_send.save()
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        except Exception as e:
            # Save email history
            history_send = HistorySendMail(
                user=None,
                name_form=form_mail.name_form,
                list_success=",".join(list_success),
                list_fail=",".join(list_fail),
                totals=len(list_success),
            )
            history_send.save()
            self.stdout.write(self.style.ERROR(f"Unexpected Error: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(
            "Mail Documents sending task completed."))
