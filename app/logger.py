# pylint: disable=invalid-name

import logging

logger = logging.getLogger('api-skeleton')


def init_logging(environment):
    levels = {
        'dev': logging.DEBUG,
        'test-internal': logging.INFO,
        'test-external': logging.INFO,
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
