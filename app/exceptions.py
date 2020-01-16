class HTTPException(Exception):
    pass


class ClientException(HTTPException):
    pass


class UnauthorisedException(ClientException):
    pass


class ForbiddenException(ClientException):
    pass
