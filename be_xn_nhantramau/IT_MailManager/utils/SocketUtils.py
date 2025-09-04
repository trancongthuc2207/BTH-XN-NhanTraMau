from django.conf import settings
import requests

DECLARE_EVENT_NAME = {
    "NOTIFICATION": "NOTIFICATION",
    "STATUS_RECEIVE_REQUEST_PAYMENT": "STATUS_RECEIVE_REQUEST_PAYMENT",
    # General
    "GENERAL_STATUS_RECEIVE_REQUEST_PAYMENT": "GENERAL_STATUS_RECEIVE_REQUEST_PAYMENT",
}


class SocketUtils:
    """ How to use:
    1. Create an instance of the SocketUtils class.
    2. Call the make_url_prepare_send_user method with the event name and optional information.
    3. Call the make_data_send method with the data you want to send.
    4. Call the send_request method to send the request.
    Example:
    socket_utils = SocketUtils(GET_VALUE_ACTION_SYSTEM("URL"))
    socket_utils.make_url_prepare_send_user("NOTIFICATION", {"id": 123})
    socket_utils.make_data_send({"message": "Hello, World!"})
    response = socket_utils.send_request()
    This will send a POST request to the specified URL with the provided data.
    Note: Make sure to replace the URL and CLIENT_ID with your actual values.
    The URL is obtained from the GET_VALUE_ACTION_SYSTEM function, and the CLIENT_ID is obtained from the settings.
    """

    def __init__(self, URL="", REQUEST=None):
        self.REQUEST = REQUEST
        self.URL = URL
        self.CLIENT_ID = settings.CLIENT_ID
        self.data_send = {
            "client_id": self.CLIENT_ID,
            "data_send": None
        }
        self.URL_PREPARE = ""

    def get_url(self):
        return self.URL

    def make_url_prepare_send_user(self, event_name, information=None):
        if information:
            id = f"{information.get('id', '')}"
            self.URL_PREPARE = f"{self.URL}api/notify/user/{event_name}/{id}"
        else:
            self.URL_PREPARE = f"{self.URL}api/notify/user/{event_name}"

    def make_url_prepare_send_general(self, event_name):
        self.URL_PREPARE = f"{self.URL}api/notify/general/{event_name}"
        # print(f"URL_PREPARE: {self.URL_PREPARE}")

    def make_data_send(self, data_send=None):
        if data_send:
            self.data_send["data_send"] = data_send
        else:
            self.data_send["data_send"] = None

    def send_request(self):
        try:
            response = requests.post(
                self.URL_PREPARE, json=self.data_send, verify=False)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            # print(f"Request failed: {e}")
            # -- LOGGING SOCKET -- #
            log = LoggingDescription(
                code_info['bug'], 'ERROR 2: Excute Socket', f"Request failed:: {str(e)}", 1)
            SOCKET_ExcuteLogging_Bug(self.REQUEST, 499, log)
            # -- LOGGING SOCKET -- #
            return None
