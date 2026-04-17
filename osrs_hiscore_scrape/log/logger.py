import logging
import threading
from collections import defaultdict

DEFAULT_LOGGER_LEVEL = logging.DEBUG
logger = {}


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter that applies color codes based on log level.

    Colors:
        DEBUG, INFO: Grey
        WARNING: Yellow
        ERROR: Red
        CRITICAL: Bold Red

    Format:
        %(asctime)s - %(levelname)-8s - %(message)s (%(filename)s:%(lineno)d)
    """
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    message_format = "%(asctime)s - %(levelname)-8s - %(message)s (%(filename)s:%(lineno)d)"

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
    def __init__(self, formatter: logging.Formatter, name: str, level: int):
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger(name=name)
        logger.setLevel(level)

        if (len(logger.handlers)):
            logger.handlers.clear()

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


def setup_custom_logger(formatter: logging.Formatter, name: str, level: int) -> LoggerWrapper:
    """ Set up a custom logger with a colorized stream handler. """
    return LoggerWrapper(formatter=formatter, name=name, level=level)


def get_logger(name: str, level: int = DEFAULT_LOGGER_LEVEL) -> LoggerWrapper:
    """ Retrieve the global custom logger instance, creating it if necessary. """
    if name not in logger:
        logger[name] = setup_custom_logger(
            formatter=CustomFormatter(), name=name, level=level)
    return logger[name]
