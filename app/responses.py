from http import HTTPStatus

from flask._compat import text_type as _

from app.i18n.base import ERROR, FAIL, SUCCESS, UNKNOWN

# HTTP codes
# Success
# 2xx
OK = int(HTTPStatus.OK)  # 200
CREATED = int(HTTPStatus.CREATED)  # 201

# Fail
# 4xx
BAD_REQUEST = int(HTTPStatus.BAD_REQUEST)  # 400
UNAUTHORIZED = int(HTTPStatus.UNAUTHORIZED)  # 401
NOT_FOUND = int(HTTPStatus.NOT_FOUND)  # 404
CONFLICT = int(HTTPStatus.CONFLICT)  # 409
UNPROCESSABLE_ENTITY = int(HTTPStatus.UNPROCESSABLE_ENTITY)  # 422

# Error
# 5xx
INTERNAL_SERVER_ERROR = int(HTTPStatus.INTERNAL_SERVER_ERROR)  # 500


def responder(code, data=None):
    if code < BAD_REQUEST:
        return dict(status=_(SUCCESS), data=data), code
    if BAD_REQUEST <= code < INTERNAL_SERVER_ERROR:
        return dict(status=_(FAIL), data=data), code
    return dict(status=_(ERROR), message=UNKNOWN), INTERNAL_SERVER_ERROR
