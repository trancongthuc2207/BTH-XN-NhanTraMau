from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import *
from ...utils.Utils import *
from general_utils.utils import split_and_clean
from ...serializers import *
from .command_util import run_command_in_background


class Command(BaseCommand):
    help = "TASK Send mail Acception to all tv has paid"

    def add_arguments(self, parser):
        parser.add_argument("list_code_hoinghi", type=str,
                            help="Danh sách code hội nghị")

    def handle(self, *args, **options):
        try:
            # Varriable
            list_code_hoinghi = split_and_clean(options["list_code_hoinghi"])
            subject_mail = GET_VALUE_ACTION_SYSTEM(
                "SET_SUBJECT_FORM_RECEPTION")
            #
            list_hoinghi_valid = []
            # print(list_code_hoinghi)
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

            # kiểm tra hội nghị còn khả dụng
            for code_hoinghi in list_code_hoinghi:
                hoinghi = DM_HoiNghi.objects.using("default").filter(
                    code_hoinghi=code_hoinghi, active=True, is_current_used=DM_HoiNghi.CURRENT_USED).first()
                if hoinghi:
                    list_hoinghi_valid.append(hoinghi.code_hoinghi)

            #
            query = Q()
            for code in list_hoinghi_valid:
                # Check if any code is in the field
                query |= Q(code_hoinghi__icontains=code)

            list_thanhvien_upload = list(
                ThanhVienUpload.objects.using("default").filter(
                    query, active=True, is_send_mail_payment=True, is_send_mail=False
                ).distinct()
            )
            #
            list_id_tv_for_send_mail = []
            for tv_upload in list_thanhvien_upload:
                list_payment_request = PaymentRequest.objects.using("default").filter(
                    user_upload=tv_upload, active=True, status="COMPLETED"
                )
                if len(list_payment_request) > 0:
                    list_id_tv_for_send_mail.append(str(tv_upload.id))

            string_id_concats = ";;".join(list_id_tv_for_send_mail)
            # print(string_id_concats)
            result_utils = process_acception_thanh_vien_upload(
                string_id_concats)
            # print(result_utils)
            # "list_code_add_success": [],
            # "list_id_fail_upload": [],
            # "string_mail_send": string_mail_send,
            if result_utils["string_mail_send"] != "":
                run_command_in_background(
                    "auto_send_mail_reception",
                    result_utils["string_mail_send"],
                    GET_VALUE_ACTION_SYSTEM(
                        "SET_SUBJECT_FORM_RECEPTION"),
                )

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected Error: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(
            "Gửi Mail xác nhận sau khi xác thực thanh toán."))
