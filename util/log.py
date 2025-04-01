import logging

logger = None


def setup_custom_logger() -> logging:
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def get_logger() -> logging:
    global logger
    logger = setup_custom_logger() if logger is None else logger
    return logger
