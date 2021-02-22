"""
Consolidates all HTTP responses the app uses. The constants are named the same as the HTTP status
codes, but this gives the ability to see at a glance all codes returned by the app. A helper
function is called for all responses from the app. Passing the HTTP code and optionally some data
creates a uniform dict response
"""

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
    """
    Pass in the HTTP code to be returned and optionally data and a dictionary is returned. 2xx codes
    will return a success; 4xx will return a failure; 5xx will return an error. 2xx and 4xx use the
    data, while 5xx will generate a message instead per the JSend spec.
    :param code: int of a HTTP status code
    :param data: dict of data to optionally add to the response
    :return: tuple of dict containing a status message (with possible data/message), then HTTP code
    """
    if code < BAD_REQUEST:
        return dict(status=_(SUCCESS), data=data), code
    if BAD_REQUEST <= code < INTERNAL_SERVER_ERROR:
        return dict(status=_(FAIL), data=data), code
    return dict(status=_(ERROR), message=UNKNOWN), INTERNAL_SERVER_ERROR
