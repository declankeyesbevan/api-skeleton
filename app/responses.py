from http import HTTPStatus

from app.i18n.base import ERROR, FAIL, SUCCESS, UNKNOWN

# HTTP codes
# Success
# 2xx
OK = HTTPStatus.OK.value  # 200
CREATED = HTTPStatus.CREATED.value  # 201

# Fail
# 4xx
BAD_REQUEST = HTTPStatus.BAD_REQUEST.value  # 400
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED.value  # 401
NOT_FOUND = HTTPStatus.NOT_FOUND.value  # 404
CONFLICT = HTTPStatus.CONFLICT.value  # 409

# Error
# 5xx
INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR.value  # 500


def responder(code, data=None):
    if code < BAD_REQUEST:
        return dict(status=SUCCESS, data=data), code
    if BAD_REQUEST <= code < INTERNAL_SERVER_ERROR:
        return dict(status=FAIL, data=data), code
    return dict(status=ERROR, message=UNKNOWN), INTERNAL_SERVER_ERROR
