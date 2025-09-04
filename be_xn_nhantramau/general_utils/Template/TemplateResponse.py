from rest_framework import status


class ResponseBase:
    # Success
    STATUS_OK = 200
    STATUS_CREATED = 201
    STATUS_ACCEPTED = 202
    STATUS_NO_CONTENT = 204

    # Client Errors
    STATUS_BAD_REQUEST = 400
    STATUS_UNAUTHORIZED = 401
    STATUS_FORBIDDEN = 403
    STATUS_NOT_FOUND = 404
    STATUS_METHOD_NOT_ALLOWED = 405
    STATUS_CONFLICT = 409
    STATUS_UNPROCESSABLE_ENTITY = 422
    STATUS_TOO_MANY_REQUESTS = 429

    # Server Errors
    STATUS_INTERNAL_SERVER_ERROR = 500
    STATUS_NOT_IMPLEMENTED = 501
    STATUS_BAD_GATEWAY = 502
    STATUS_SERVICE_UNAVAILABLE = 503
    STATUS_GATEWAY_TIMEOUT = 504

    # Custom Defaults
    STATUS_SUCCESS_DEFAULT = STATUS_OK
    STATUS_ERROR_DEFAULT = 499  # Custom error (can use 520 instead)

    def __init__(
        self,
        data=None,
        message='',
        list_errors=None,
        status_code=STATUS_SUCCESS_DEFAULT,
    ):
        self.data = data if data is not None else []
        self.message = message
        self.list_errors = list_errors if list_errors is not None else [
            {
                "entities_error": [],
                "servers_error": [],
            }
        ]
        self.status_code = status_code

    def add_error(self, data):
        # Ensure list_errors has at least one dictionary
        if not self.list_errors:
            self.list_errors.append(
                {"entities_error": [], "servers_error": []})

        # Add the message to the servers_error list of the first dictionary
        self.list_errors[0]["servers_error"].append(data)

    def add_entities_error(self, data):
        # Ensure list_errors has at least one dictionary
        if not self.list_errors:
            self.list_errors.append(
                {"entities_error": [], "servers_error": []})

        # Add the message to the servers_error list of the first dictionary
        self.list_errors[0]["entities_error"].append(data)

    def set_data(self, data):
        self.data = data

    def set_message(self, message: str):
        self.message = message

    def set_status(self, status_code: int):
        self.status_code = status_code

    def is_success(self) -> bool:
        return 200 <= self.status_code < 300 and not self.list_errors

    def get(self) -> dict:
        return {
            "data": self.data,
            "message": self.message,
            "list_errors": self.list_errors,
            "status_code": self.status_code,
        }

    # Returns a tuple of the response data and the appropriate HTTP status code
    def return_response(self):
        match self.status_code:
            case self.STATUS_OK:
                status_response = status.HTTP_200_OK
            case self.STATUS_CREATED:
                status_response = status.HTTP_201_CREATED
            case self.STATUS_UNAUTHORIZED:
                status_response = self.STATUS_UNAUTHORIZED
            case default:
                status_response = status.HTTP_417_EXPECTATION_FAILED
        data = {
            "data_response": self.get(),
            "status_response": status_response,
        }
        return data

    def __str__(self):
        return str(self.get())

# res = ResponseBase()
# res.set_data({"user": "John"})
# res.set_status(ResponseBase.STATUS_CREATED)
# res.set_message("User successfully created")
