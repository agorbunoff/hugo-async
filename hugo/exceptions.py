class HttpError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
