from flask_babel import lazy_gettext as _

# Status
SUCCESS = _('success')
FAIL = _('fail')
ERROR = _('error')

# Messages
# Success
# 2xx
LOGIN_SUCCESS = _('Successfully logged in')
LOGOUT_SUCCESS = _('Successfully logged out')
USER_LIST_SUCCESS = _('Successfully listed user')
USERS_LIST_SUCCESS = _('Successfully listed users')
USER_CREATE_SUCCESS = _('Successfully created user')
EMAIL_CONFIRMED = _('Thank you for confirming your email address')

# Fail
# 4xx
MALFORMED = _('Request malformed')
EMAIL_PASSWORD = _('Email and password do not match')
EMAIL_NOT_CONFIRMED = _('Email address not confirmed')
CANNOT_VIEW_OTHERS = _('Non-admin users can only view themselves')
JWT_ERROR = _('JWT error')
JWT_EXPIRED = _('JWT signature expired: log in again')
JWT_INVALID = _('JWT invalid: log in again')
JWT_BLACKLISTED = _('JWT blacklisted: log in again')
JWT_UNPROCESSABLE = _('JWT malformed')
JWT_REQUIRED = _('JWT token with admin privileges required to create admin')
JWT_INSUFFICIENT = _('User has insufficient privilege to create to create admin')
CONFIRMATION_FAILED = _('Email confirmation failed')
USER_NOT_FOUND = _('User not found')
USER_EXISTS = _('User exists: log in')
ACCOUNT_ALREADY_CONFIRMED = _('Account already confirmed: log in')

# Error
# 5xx
UNKNOWN = _('Unknown error: try again')
FINDING_USER = _('Error finding user by')
GETTING_USER = _('Error getting all users')
GETTING_USERS = _('Error getting a user')
ENCODING_JWT = _('Error encoding JWT token')
SAVING_TO_DATABASE = _('Error saving to database')
TOKEN_BLACKLIST = _('Error getting token blacklist')

# Email
CONFIRM = _('Confirm Your Email Address')
PLAINTEXT_EMAIL_BODY = """
Your account on API Skeleton was successfully created.
Please click the link below to confirm your email address and
activate your account:
  
{url}
 
Questions? Comments? Email Us: {email}
"""
