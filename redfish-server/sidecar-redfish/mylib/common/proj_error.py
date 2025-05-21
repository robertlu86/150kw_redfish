from http import HTTPStatus

class ProjError(Exception):
    def __init__(self, code: HTTPStatus, message: str):
        self.code = code
        self.message = message
    