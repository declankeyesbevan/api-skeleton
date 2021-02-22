# pylint: disable=invalid-name

"""
Defined logging level depending on the environment.
"""

import logging

logger = logging.getLogger('api-skeleton')


def init_logging(environment):
    """
    Pass in the environment and the appropriate logging level is set. Development is debug and all
    others are info. Adds a formatter to help with reading the messages. It output the level of the
    logging; the module; the line number; the message. It is also spaced so all log messages begin
    in the same column.
    :param environment: string of the required environment
    """
    levels = {
        'dev': logging.DEBUG,
        'test-in-memory': logging.INFO,
        'test-deployed': logging.INFO,
        'prod': logging.INFO,
    }
    logger.setLevel(levels.get(environment))

    handler = logging.StreamHandler()
    # Separate the sections of the message by padding them.
    formatter = logging.Formatter('%(levelname)-8s %(module)-20s %(lineno)04d %(message)s')
    handler.setFormatter(formatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
