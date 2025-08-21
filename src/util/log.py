import functools
import inspect
import logging
from typing import Callable

logger = None


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter that applies color codes based on log level.

    Colors:
        DEBUG, INFO: Grey
        WARNING: Yellow
        ERROR: Red
        CRITICAL: Bold Red

    Format:
        %(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)
    """
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        """
        Format a log record with the color corresponding to its level.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted and colorized log message.
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_custom_logger() -> logging:
    """
    Set up a custom logger with a colorized stream handler.

    Returns:
        logging.Logger: Configured logger instance with DEBUG level and custom formatting.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def get_logger() -> logging:
    """
    Retrieve the global custom logger instance, creating it if necessary.

    Returns:
        logging.Logger: The global logger instance.
    """     
    global logger
    logger = setup_custom_logger() if logger is None else logger
    return logger


def finished_script(callback: Callable):
    """
    Decorator that logs when a (async) method has finished.

    Args:
        callback (Callable): The function to wrap.

    Returns:
        Callable: An asynchronous wrapper coroutine.
    """
    @functools.wraps(callback)
    async def wrapper(*args, **kwargs):
        result = callback(*args, **kwargs)
        if inspect.isawaitable(result):
            result = await result

        get_logger().info("done")
        return result
    return wrapper
