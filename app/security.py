"""
Utilities for increasing security in the package.
"""
# pylint: disable=invalid-name

import logging
from string import ascii_lowercase, ascii_uppercase, digits

from app.utils import SPECIAL_CHARACTERS

logger = logging.getLogger('api-skeleton')


def remove(payload, to_remove):
    """
    Remove items from a dictionary so sensitive values aren't logged. Does not affect passed dict.

    :param payload: JSON payload
    :type payload: :class: `dict`
    :param to_remove: Keys to redact
    :type to_remove: :class: `list`
    :return: JSON payload with keys removed
    :rtype: :class: `dict`
    """
    logger.info("Removing item(s) from payload")

    return {k: v for k, v in payload.items() if k not in to_remove}


class PasswordValidator:
    # Liberally stolen from here:
    # https://codereview.stackexchange.com/questions/165187/password-checker-in-python

    MIN_LENGTH = 12

    @classmethod
    def contains(cls, required_chars, s):
        return any(c in required_chars for c in s)

    @classmethod
    def contains_upper(cls, s):
        return cls.contains(ascii_uppercase, s)

    @classmethod
    def contains_lower(cls, s):
        return cls.contains(ascii_lowercase, s)

    @classmethod
    def contains_digit(cls, s):
        return cls.contains(digits, s)

    @classmethod
    def contains_special(cls, s):
        return cls.contains(SPECIAL_CHARACTERS, s)

    @classmethod
    def length(cls, s):
        return len(s) >= cls.MIN_LENGTH

    @classmethod
    def validate_password(cls, password):
        validations = (
            (cls.contains_upper, 'Password needs at least one upper-case character.'),
            (cls.contains_lower, 'Password needs at least one lower-case character.'),
            (cls.contains_digit, 'Password needs at least one number.'),
            (cls.contains_special, 'Password needs at least one special character.'),
            (cls.length, f'Password needs to be at least {cls.MIN_LENGTH} characters in length.'),
        )
        return [msg for validator, msg in validations if not validator(password)]
