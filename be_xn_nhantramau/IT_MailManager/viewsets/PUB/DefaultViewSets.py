import base64
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response, APIView
from IT_MailManager.models import *
from IT_MailManager.serializers import *
from datetime import datetime
from IT_OAUTH.throttles import *
from django.conf import settings
from django.shortcuts import render
from IT_MailManager.utils.ResponseMessage import *
from IT_MailManager.perms import *
from IT_MailManager.utils.CodeGenerate import *
from IT_OAUTH.models import User
from IT_OAUTH.serializers import *
from IT_MailManager.paginations import Paginations
from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

# Command imports
from IT_MailManager.management.commands.command_util import run_command_in_background
from IT_MailManager.Service.mail_service import test

# Template imports
from IT_MailManager.Template.TemplateFormDataMail import EmailSetup

# Utils
from IT_MailManager.utils.Utils import CHECK_LIST_ID_FILES_ON_SERVER_BEFORE_SEND, get_base64_from_file, GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD
from general_utils.Template.TemplateResponse import ResponseBase
from general_utils.Logging.logging_tools import LogHelper
from general_utils.utils import *

# Logger sys
logger_info_sys = LogHelper("file_info_sys")
logger_bug_sys = LogHelper("file_bug_sys")

# /(?P<id>[a-zA-Z0-9]+)
# Khoa Khám Bệnh


class DefaultViewSetBase(
    viewsets.ViewSet,
):
    queryset = User.objects.using("oauth").all()
    throttle_classes = [SuperRateThrottle]
    # serializer_class = UserSerializer
    parser_classes = [
        parsers.MultiPartParser,
    ]

    def get_permissions(self):
        if self.action in []:
            return [RoleAppDefault()]

        return [permissions.AllowAny()]

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------ GET ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    # Màn hình lấy mẫu của các phòng khám
    @action(methods=["get"], detail=False, url_path="get/ds-khoaphong", name="")
    def get_ds_khoaphong(self, request):
        # init response
        response = {}

        # Dieu kien
        where = {
            "sodong": "",
        }

        page_config = {"from": 0, "amount": Paginations.NUM_PAGES_DEFAULT}

        # Set dieu kien
        # sodong = request.query_params.get('sodong')
        # if sodong:
        #    where['sodong'] = sodong

        response["data"] = {
            "ds_khoaphong": "this is a placeholder for the list of departments",
        }
        response["message"] = "Successfully retrieved the list of departments."
        response["status_code"] = 200

        return Response(response, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #
    # ----------------------------------- POST ------------------------------------- #
    # ------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------ #

    @action(methods=["post"], detail=False, url_path="hash/create", name="")
    def POST_create_hash_password(self, request):
        # init response
        response = ResponseBase()
        try:
            prefix = "pbkdf2_sha256$0e0ac3288f01261829d359a3b3c58dc2$"
            data_body = request.data
            str_hash = encode_with_prefix(
                input_text=data_body["str_raw"], prefix=prefix
            )

            # return response
            response.set_data(
                {"str_raw": data_body["str_raw"], "str_hash": str_hash})
            response.set_message("Tạo thành công!")
            response.set_status(ResponseBase.STATUS_CREATED)
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Tạo không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            response.add_error({"error": str(e)})

        return Response(
            data=response.return_response()["data_response"],
            status=response.return_response()["status_response"],
        )

    @action(methods=["post"], detail=False, url_path="mail/send-mail", name="")
    def POST_send_mail_by_template(self, request):
        # init response
        response = ResponseBase()
        try:
            data_body = request.data

            form_mail = (
                FormMail.objects.using("default")
                .filter(name_form=data_body["form_mail_name"])
                .first()
            )
            if not form_mail:
                response.set_message(
                    f"FormMail template '{data_body['form_mail_name']}' not found."
                )
                response.set_status(ResponseBase.STATUS_NOT_FOUND)
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

            # List varribles in the template
            varriables = extract_template_variables(form_mail.value)
            print(varriables)
            # List cid
            list_cid = extract_cid_variables(form_mail.value)
            # print(list_cid)

            # Initialize containers
            recipients = []
            attachments = {}
            body_images = {}
            template_data = {}
            list_img_embedded_cid = []
            files_for_send_on_server = []
            files_for_send_on_client = []

            # This loop processes data from 'Content-Type: multipart/form-data'
            # It checks if specific keys are JSON strings and decodes them.
            for key, value in data_body.items():
                if key == "recipients":
                    recipients = json.loads(value) if isinstance(
                        value, str) else value
                elif key == "template_data":
                    template_data = (
                        json.loads(value) if isinstance(value, str) else value
                    )
                elif key == "files_for_send_on_server":
                    files_for_send_on_server = (
                        json.loads(value) if isinstance(value, str) else value
                    )
                elif key == "list_img_embedded_cid":
                    # New logic to handle a dictionary.
                    list_img_embedded_cid = (
                        json.loads(value) if isinstance(value, str) else value
                    )
                    if isinstance(list_img_embedded_cid, dict):
                        for cid_key, cid_value in list_img_embedded_cid.items():
                            body_images[cid_key] = cid_value
                elif key == "subject":
                    subject = value

            # Validate required fields
            if not recipients or not subject:
                response.set_message("Recipients and subject are required.")
                response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                response.add_error({"error": str(e)})
                return Response(
                    data=response.return_response()["data_response"],
                    status=response.return_response()["status_response"],
                )

            # Validate that all required variables are provided
            for var in varriables:
                if var not in template_data:
                    response.set_message(f"Missing required variable: {var}")
                    response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                    response.add_error({"error": f"Missing variable: {var}"})
                    return Response(
                        data=response.return_response()["data_response"],
                        status=response.return_response()["status_response"],
                    )

            # --- FILE HANDLING ---
            # Assuming you have a file size limit, for example, 20MB.
            MAX_UPLOAD_SIZE, NUM_MB = GET_CONFIG_MAXIMUM_DATA_FOR_UPLOAD()

            if request.FILES:
                # Loop through each file in the request.FILES dictionary.
                for file_key, file_object in request.FILES.items():
                    # Add a check for file size before processing.
                    if file_object.size > MAX_UPLOAD_SIZE:
                        # Handle the error, e.g., return a JSON response with an error message.
                        # In a real application, you would handle this error more gracefully.
                        # For this example, we'll just skip the file.
                        response.add_error(
                            {"error": f"File '{file_object.name}' vượt quá {NUM_MB} MB cho phép."})
                        response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                        return Response(
                            data=response.return_response()["data_response"],
                            status=response.return_response()[
                                "status_response"],
                        )

                    # Read the file's content as a bytes object.
                    file_content_bytes = file_object.read()

                    # Encode the bytes into a Base64 string.
                    base64_string = base64.b64encode(
                        file_content_bytes).decode("utf-8")

                    # Store the Base64 string in the attachments dictionary.
                    # The key is the original file name.
                    attachments[file_object.name] = base64_string

            # Handle file on server
            if files_for_send_on_server:
                check_file, list_files_error, list_files = CHECK_LIST_ID_FILES_ON_SERVER_BEFORE_SEND(
                    files_for_send_on_server)
                if not check_file:
                    for err in list_files_error:
                        response.add_error({"error": str(err)})
                    # return err
                    response.set_message(
                        f"Gặp lỗi trong quá trình kiểm tra files trên máy chủ!")
                    response.set_status(ResponseBase.STATUS_BAD_REQUEST)
                    return Response(
                        data=response.return_response()["data_response"],
                        status=response.return_response()["status_response"],
                    )

                # Nếu có files
                if list_files:
                    for file in list_files:
                        if file.file_name:
                            base64_file, error_file = get_base64_from_file(
                                file.file.path)
                            if base64_file:
                                attachments[file.file_name] = base64_file
                            else:
                                raise ValueError(
                                    f"Lỗi mã hóa chuyển đổi file của ID: {file.pk}")
                        else:
                            raise ValueError(
                                f"Không tìm thấy tên file của ID: {file.pk}")

            # Create an instance of the EmailSetup class
            email_config = EmailSetup(
                recipients=recipients,
                subject=subject,
                template_data=template_data,
                attachments=attachments,
                body_images=body_images,
            )

            run_command_in_background(
                "command_send_mail",
                form_mail.name_form,
                context_json=json.dumps(
                    email_config.to_api_payload(), ensure_ascii=False
                ),
            )

            # return response
            response.set_data(None)
            response.set_message("Tạo thành công!")
            response.set_status(ResponseBase.STATUS_CREATED)
        except Exception as e:
            # Exception Set Data
            response.set_data(None)
            response.set_message("Tạo không thành công!")
            response.set_status(ResponseBase.STATUS_BAD_REQUEST)
            response.add_error({"error": str(e)})

        return Response(
            data=response.return_response()["data_response"],
            status=response.return_response()["status_response"],
        )
