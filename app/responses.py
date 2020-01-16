from http import HTTPStatus

# HTTP codes
# 2xx
OK = HTTPStatus.OK.value  # 200
CREATED = HTTPStatus.CREATED.value  # 201

# 4xx
BAD_REQUEST = HTTPStatus.BAD_REQUEST.value  # 400
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED.value  # 401
FORBIDDEN = HTTPStatus.FORBIDDEN.value  # 403
NOT_FOUND = HTTPStatus.NOT_FOUND.value  # 404
CONFLICT = HTTPStatus.CONFLICT.value  # 409

# 5xx
INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR.value  # 500

# Status
SUCCESS = 'success'
FAIL = 'fail'

# Messages
# Success
LOGIN_SUCCESS = 'Successfully logged in.'
LOGOUT_SUCCESS = 'Successfully logged out.'
REGISTRATION_SUCCESS = 'Successfully registered.'
USERS_LIST_SUCCESS = 'Users successfully listed.'
USER_LIST_SUCCESS = 'User successfully listed.'
CREATE_SUCCESS = 'User successfully created.'

# Fail
EMAIL_OR_PASSWORD = 'Email or password do not match.'
UNKNOWN = 'Unknown error. Try again.'
AUTH_TOKEN = 'Provide a valid auth token.'
USER_EXISTS = 'User already exists. Please Log in.'
USER_NOT_FOUND = 'User not found.'
MALFORMED = 'Malformed data passed.'

# Payloads
# Success
LOGOUT_SUCCESS_PAYLOAD = dict(status=SUCCESS, message=LOGOUT_SUCCESS), OK

# Fail
# 4xx
MALFORMED_PAYLOAD = dict(status=FAIL, message=MALFORMED), BAD_REQUEST
UNAUTHORISED_PAYLOAD = dict(status=FAIL, message=EMAIL_OR_PASSWORD), UNAUTHORIZED
CONFLICT_PAYLOAD = dict(status=FAIL, message=USER_EXISTS), CONFLICT

# 5xx
UNKNOWN_ERROR_PAYLOAD = dict(status=FAIL, message=UNKNOWN), INTERNAL_SERVER_ERROR
