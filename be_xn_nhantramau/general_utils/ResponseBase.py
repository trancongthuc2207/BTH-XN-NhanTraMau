class ResponseBase:
    data = []
    message = ''
    list_errors = []
    status_code = 200
    # Status code
    STATUS_ERROR_DEFAULT = 499
    STATUS_SUCCESS_DEFAULT = 200

    def __init__(self, data=[], message='', list_errors=[], status_code=499):
        self.data = data
        self.message = message
        self.list_errors = list_errors
        self.status_code = status_code

    def get(self):
        res = {
            'data': self.data,
            'message': self.message,
            'list_errors': self.list_errors,
            'status_code': self.status_code,
        }
        return res
