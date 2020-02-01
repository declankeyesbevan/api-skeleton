from http import HTTPStatus

# Status
SUCCESS = 'success'
FAIL = 'fail'
ERROR = 'error'


# HTTP codes
# Success
# 2xx
OK = HTTPStatus.OK.value  # 200
CREATED = HTTPStatus.CREATED.value  # 201

# Fail
# 4xx
BAD_REQUEST = HTTPStatus.BAD_REQUEST.value  # 400
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED.value  # 401
FORBIDDEN = HTTPStatus.FORBIDDEN.value  # 403
NOT_FOUND = HTTPStatus.NOT_FOUND.value  # 404
CONFLICT = HTTPStatus.CONFLICT.value  # 409

# Error
# 5xx
INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR.value  # 500


# Messages
# Success
# 2xx
USER_CREATE_SUCCESS = 'Created user success'
USER_LIST_SUCCESS = 'Listed user success'
USERS_LIST_SUCCESS = 'Listed users success'
LOGIN_SUCCESS = 'Logged in success'
LOGOUT_SUCCESS = 'Logged out success'

# Fail
# 4xx
MALFORMED = 'Malformed data passed'
EMAIL_OR_PASSWORD = 'Email and password do not match'
USER_NOT_FOUND = 'User not found'
USER_EXISTS = 'User exists: log in'
SIGNATURE_EXPIRED = 'Signature expired: log in again'
INVALID_TOKEN = 'Invalid token: log in again'
TOKEN_BLACKLISTED = 'Token blacklisted: log in again'

# Error
# 5xx
UNKNOWN = 'Unknown error: try again'


# Payloads
# Success
LOGOUT_SUCCESS_PAYLOAD = dict(status=SUCCESS, data=None), OK

# Fail
# 4xx
MALFORMED_PAYLOAD = dict(status=FAIL, data=dict(malformed=MALFORMED)), BAD_REQUEST
UNAUTHORISED_PAYLOAD = dict(status=FAIL, data=dict(credentials=EMAIL_OR_PASSWORD)), UNAUTHORIZED
CONFLICT_PAYLOAD = dict(status=FAIL, data=dict(user=USER_EXISTS)), CONFLICT

# Error
# 5xx
UNKNOWN_ERROR_PAYLOAD = dict(status=ERROR, message=UNKNOWN), INTERNAL_SERVER_ERROR
