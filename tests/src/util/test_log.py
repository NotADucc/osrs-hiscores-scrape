import asyncio
import logging
import pytest

from src.util.log import CustomFormatter, log_execution, get_logger, setup_custom_logger


@pytest.fixture
def logger_instance():
    """Provide a fresh logger instance for each test."""
    return setup_custom_logger(CustomFormatter())


def test_get_logger_singleton():
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2


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


def test_log_execution_sync(caplog):
    caplog.set_level(logging.DEBUG)

    @log_execution
    def sample_sync(x, y):
        return x + y

    result = sample_sync(2, 3)
    assert result == 5

    logs = [rec.message for rec in caplog.records]
    assert "start: sample_sync" in logs
    assert "finished: sample_sync" in logs
    assert any("log type count" in msg for msg in logs)


@pytest.mark.asyncio
async def test_log_execution_async(caplog):
    caplog.set_level(logging.DEBUG)

    @log_execution
    async def sample_async(x, y):
        await asyncio.sleep(0.01)
        return x + y

    result = await sample_async(2, 3)
    assert result == 5

    logs = [rec.message for rec in caplog.records]
    assert "start: sample_async" in logs
    assert "finished: sample_async" in logs
    assert any("log type count" in msg for msg in logs)


def test_custom_formatter_colors():
    formatter = CustomFormatter()
    record = logging.LogRecord(
        name="test", level=logging.ERROR, pathname=__file__,
        lineno=123, msg="test error", args=(), exc_info=None
    )
    formatted = formatter.format(record)
    assert "test error" in formatted
    assert "\x1b[31;20m" in formatted  # red color
