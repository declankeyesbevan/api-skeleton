from flask_babel import lazy_gettext as _

# Status
SUCCESS = _('success')
FAIL = _('fail')
ERROR = _('error')

# Messages
# Success
# 2xx
USER_CREATE_SUCCESS = _('Successfully created user')
USER_LIST_SUCCESS = _('Successfully listed user')
USERS_LIST_SUCCESS = _('Successfully listed users')
LOGIN_SUCCESS = _('Successfully logged in')
LOGOUT_SUCCESS = _('Successfully logged out')

# Fail
# 4xx
# TODO: move JWT errors in here: 'Error encoding JWT token' etc
MALFORMED = _('Request malformed')
EMAIL_PASSWORD = _('Email and password do not match')
USER_NOT_FOUND = _('User not found')
USER_EXISTS = _('User exists: log in')
JWT_EXPIRED = _('JWT signature expired: log in again')
JWT_INVALID = _('JWT invalid: log in again')
JWT_BLACKLISTED = _('JWT blacklisted: log in again')
JWT_UNPROCESSABLE = _('JWT malformed')

# Error
# 5xx
UNKNOWN = _('Unknown error: try again')
