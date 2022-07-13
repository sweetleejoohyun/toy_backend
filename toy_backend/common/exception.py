class CustomException(Exception):
    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message

    def to_dict(self):
        exception_result = dict()
        exception_result['error_message'] = self.error_message
        return exception_result


class UploadError(CustomException):
    pass


class UploadFileRequired(UploadError):
    def __init__(self, error_message):
        status_code = 400
        super().__init__(status_code, error_message)


class UploadFilenameRequired(UploadError):
    def __init__(self, error_message):
        status_code = 400
        super().__init__(status_code, error_message)


class UploadImageFileRequired(UploadError):
    def __init__(self, error_message):
        status_code = 400
        super().__init__(status_code, error_message)


class UploadVideoFileRequired(UploadError):
    def __init__(self, error_message):
        status_code = 400
        super().__init__(status_code, error_message)


class FailedToUploadFile(UploadError):
    def __init__(self, error_message):
        status_code = 400
        super().__init__(status_code, error_message)