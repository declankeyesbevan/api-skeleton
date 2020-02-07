"""
Utilities for increasing security in the package.
"""
import logging

# pylint: disable=invalid-name

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
