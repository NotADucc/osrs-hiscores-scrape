from collections import defaultdict
import functools
import inspect
import logging
import threading
from typing import Callable

LOGGER_LEVEL = logging.DEBUG
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


class LoggerWrapper:
    def __init__(self):
        handler = logging.StreamHandler()
        handler.setFormatter(CustomFormatter())

        logger = logging.getLogger('logger')
        logger.setLevel(LOGGER_LEVEL)
        logger.addHandler(handler)

        self.logger = logger
        self._counts = defaultdict(int)
        self._lock = threading.Lock()

    def _log(self, level: str, msg: str, *args, **kwargs):
        with self._lock:
            self._counts[level] += 1
        getattr(self.logger, level.lower())(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._log("INFO", msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._log("WARNING", msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._log("ERROR", msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._log("DEBUG", msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._log("CRITICAL", msg, *args, **kwargs)

    def get_counts(self):
        with self._lock:
            return dict(self._counts)


def setup_custom_logger() -> LoggerWrapper:
    """
    Set up a custom logger with a colorized stream handler.

    Returns:
        LoggerWrapper: Configured logger instance with DEBUG level and custom formatting.
    """
    return LoggerWrapper()


def get_logger() -> LoggerWrapper:
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
    Decorator that logs when a (async) method has finished, also displays the count of logs per type.

    Args:
        callback (Callable): The function to wrap.

    Returns:
        Callable: An asynchronous wrapper coroutine.
    """
    @functools.wraps(callback)
    async def wrapper(*args, **kwargs):
        try: 
            result = callback(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
        except KeyboardInterrupt:
            raise
        finally:
            get_logger().info(get_logger().get_counts())
            get_logger().info("done")

        return result
    
    return wrapper
