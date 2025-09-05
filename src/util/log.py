import asyncio
import functools
import inspect
import logging
import threading
from collections import defaultdict
from typing import Any, Callable, TypeVar, cast

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
    message_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + message_format + reset,
        logging.INFO: grey + message_format + reset,
        logging.WARNING: yellow + message_format + reset,
        logging.ERROR: red + message_format + reset,
        logging.CRITICAL: bold_red + message_format + reset
    }

    def format(self, record):
        """ Format a log record with the color corresponding to its level. """
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
        kwargs.setdefault("stacklevel", 3)
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
    """ Set up a custom logger with a colorized stream handler. """
    return LoggerWrapper()


def get_logger() -> LoggerWrapper:
    """ Retrieve the global custom logger instance, creating it if necessary. """
    global logger
    logger = setup_custom_logger() if logger is None else logger
    return logger


T = TypeVar("T", bound=Callable[..., Any])


def finished_script(func: T) -> T:
    """Decorator that logs when a (async) or (sync) method has finished,
    also displays the count of logs per type.
    """
    async def message_wrapper(*args, **kwargs):
        logger = get_logger()
        try:
            logger.info("start script")
            result = await func(*args, **kwargs)
        except KeyboardInterrupt:
            raise
        finally:
            logger.info("finished script")
            logger.debug(f"log type count: {logger.get_counts()}")
        return result

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await message_wrapper(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        return asyncio.run(message_wrapper(*args, **kwargs))

    return cast(T, async_wrapper) if inspect.iscoroutinefunction(func) \
        else cast(T, sync_wrapper)
