from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import *
from ...utils.Utils import *


class Command(BaseCommand):
    help = "Send emails with merged participant information."

    # email :: id_tv_upload :: hoten :: link :: image ;;
    def add_arguments(self, parser):
        # hoten:: ;;
        parser.add_argument(
            "list_mail", type=str, help="List of mails separated by ';;'"
        )
        parser.add_argument("subject_mail", type=str,
                            help="Subject of the email")

    def handle(self, *args, **options):
        list_mail = options["list_mail"]
        subject_mail = options["subject_mail"]

        list_success = []
        list_fail = []
        list_id_success = []
        list_id_fail = []

        try:
            # Get form mail template
            form_mail = (
                FormMail.objects.using("default")
                .filter(
                    id=GET_VALUE_ACTION_SYSTEM(
                        "SET_ID_FORM_PAYMENT_REQUEST_EACH_HN"),
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
            list_person = []
            mails = list_mail.split(";;")
            for mail in mails:
                if mail:
                    parts = mail.split("::")
                    if len(parts) != 8:
                        continue  # Skip invalid entries
                    parts_dict = {
                        "mail_string": parts[0],
                        "id_tv_upload_string": parts[1],
                        "hoten_string": parts[2],
                        "link": f"<a href='{parts[3]}' style='text-transform: uppercase; font-weight: bolder; font-size: 16px'>đường dẫn truy cập trang thanh toán.</a>",
                        "image_string": parts[4],
                        "price_hn": parts[5],
                        "price_image_hn": parts[6],
                        "ten_hn": parts[7],
                    }

                    list_person.append(parts_dict)
                    self.stdout.write(
                        self.style.SUCCESS(parts_dict["id_tv_upload_string"])
                    )
            # self.stdout.write(self.style.SUCCESS(list_mail))
            # Sending merged emails
            outlook = settings.OUTLOOK_MAIL_RECEPTION
            for p in list_person:
                # init
                content_form = ""

                # kiểm tra nếu form 4 - gửi qr bệnh viện + stk
                if GET_VALUE_ACTION_SYSTEM("SET_ID_FORM_PAYMENT_REQUEST_EACH_HN") in ["4", "7"]:
                    content_form = form_mail.value.format(
                        hoten=p["hoten_string"],
                        noidung=p["link"],
                        # my_image="""{{my_image}}""",
                        so_tai_khoan=GET_VALUE_ACTION_SYSTEM(
                            "SET_STK_BV_FOR_SEND_MAIL_PAYMENT_REQUEST"
                        ),
                        qr_gia_hn="""{{qr_gia_hn}}""",
                        ten_hn=p["ten_hn"],
                        price_hn=p["price_hn"]
                    )
                else:
                    content_form = form_mail.value.format(
                        hoten=p["hoten_string"],
                        noidung=p["link"],
                        # my_image="""{{my_image}}""",
                    )
                try:
                    # data_as_bytes = base64.b64decode(
                    #     p["image_string"].split(",")[1])
                    # Nếu mail form thuộc 4 - QR CODE BỆNH VIỆN + STK
                    if GET_VALUE_ACTION_SYSTEM("SET_ID_FORM_PAYMENT_REQUEST_EACH_HN") in ["4", "7"]:
                        data_as_bytes_qr_gia_hn = base64.b64decode(
                            p["price_image_hn"].split(",")[1]
                        )
                        outlook.send(
                            receivers=[p["mail_string"]],
                            subject=subject_mail,
                            html=content_form,
                            attachments={},
                            body_images={
                                # "my_image": data_as_bytes,
                                "qr_gia_hn": data_as_bytes_qr_gia_hn,
                            },
                        )
                    # Không QR + STK
                    else:
                        outlook.send(
                            receivers=[p["mail_string"]],
                            subject=subject_mail,
                            html=content_form,
                            attachments={},
                            body_images={
                                # "my_image": data_as_bytes
                            },
                        )
                    list_success.append(p["id_tv_upload_string"])
                    list_id_success.append(p["id_tv_upload_string"])

                    # Update database record
                    thanhvien_upload = (
                        ThanhVienUpload.objects.using("default")
                        .filter(id=p["id_tv_upload_string"])
                        .first()
                    )
                    if thanhvien_upload:
                        thanhvien_upload.is_send_mail_payment = True
                        thanhvien_upload.save()

                except Exception as e:
                    list_fail.append(p["id_tv_upload_string"])
                    list_id_fail.append(p["id_tv_upload_string"])
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to send email to {p['mail_string']}: {e}"
                        )
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

        self.stdout.write(self.style.SUCCESS("Mail sending task completed."))
