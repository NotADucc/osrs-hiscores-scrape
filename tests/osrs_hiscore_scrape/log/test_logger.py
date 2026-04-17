import logging

import pytest

from osrs_hiscore_scrape.log.logger import (CustomFormatter, get_logger,
                                            setup_custom_logger)


@pytest.fixture
def logger_instance():
    """Provide a fresh logger instance for each test."""
    return setup_custom_logger(CustomFormatter(), __name__, logging.DEBUG)


def test_get_logger_same_name():
    logger1 = get_logger(__name__)
    logger2 = get_logger(__name__)
    assert logger1 is logger2


def test_get_logger_different_name():
    logger1 = get_logger(__name__)
    logger2 = get_logger('test')
    assert logger1 is not logger2


def test_logger_counts(logger_instance, caplog):
    caplog.set_level(logging.DEBUG)

    logger_instance.info("info msg")
    logger_instance.warning("warning msg")
    logger_instance.error("error msg")
    logger_instance.debug("debug msg")
    logger_instance.critical("critical msg")

    counts = logger_instance.get_counts()
    assert counts["INFO"] == 1
    assert counts["WARNING"] == 1
    assert counts["ERROR"] == 1
    assert counts["DEBUG"] == 1
    assert counts["CRITICAL"] == 1

    messages = [rec.message for rec in caplog.records]
    assert "info msg" in messages
    assert "warning msg" in messages
    assert "error msg" in messages
    assert "debug msg" in messages
    assert "critical msg" in messages


def test_custom_formatter_colors():
    formatter = CustomFormatter()
    record = logging.LogRecord(
        name="test", level=logging.ERROR, pathname=__file__,
        lineno=123, msg="test error", args=(), exc_info=None
    )
    formatted = formatter.format(record)
    assert "test error" in formatted
    assert "\x1b[31;20m" in formatted  # red color
