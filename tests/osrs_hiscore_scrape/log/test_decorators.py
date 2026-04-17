import asyncio
import logging
from unittest.mock import patch

import pytest

from osrs_hiscore_scrape.log.decorators import log_lifecycle, profile_execution


@pytest.mark.asyncio
async def test_profile_execution_async_function():
    async def dummy_async(x):
        await asyncio.sleep(0.01)
        return x * 2

    with patch("osrs_hiscore_scrape.util.mem_profile.memory_usage_psutil", side_effect=[100.0, 105.0]), \
            patch("time.perf_counter", side_effect=[1.0, 2.0]), \
            patch("osrs_hiscore_scrape.log.logger.LoggerWrapper.debug") as mock_logger:

        wrapped = profile_execution(dummy_async)
        result = await wrapped(5)

        assert result == 10

        assert mock_logger.call_count == 3

        calls = [call[0][0] for call in mock_logger.call_args_list]

        assert "[test_decorators.py] - dummy_async took 0:00:01" in calls[0]
        assert "Python peak memory:" in calls[1]
        assert "OS-level memory: 5.000000 MB" in calls[2]


@pytest.mark.asyncio
async def test_profile_execution_sync_function():
    def dummy_sync(x):
        return x * 2

    with patch("osrs_hiscore_scrape.util.mem_profile.memory_usage_psutil", side_effect=[100.0, 105.0]), \
            patch("time.perf_counter", side_effect=[1.0, 2.0]), \
            patch("osrs_hiscore_scrape.log.logger.LoggerWrapper.debug") as mock_logger:

        wrapped = profile_execution(dummy_sync)
        result = await wrapped(5)

        assert result == 10

        assert mock_logger.call_count == 3

        calls = [call[0][0] for call in mock_logger.call_args_list]

        assert "[test_decorators.py] - dummy_sync took 0:00:01" in calls[0]
        assert "Python peak memory:" in calls[1]
        assert "OS-level memory: 5.000000 MB" in calls[2]


def test_log_lifecycle_sync(caplog):
    caplog.set_level(logging.DEBUG)

    @log_lifecycle
    def sample_sync(x, y):
        return x + y

    result = sample_sync(2, 3)
    assert result == 5

    logs = [rec.message for rec in caplog.records]
    assert "start: sample_sync" in logs
    assert "finished: sample_sync" in logs
    assert any("log type count" in msg for msg in logs)


@pytest.mark.asyncio
async def test_log_lifecycle_async(caplog):
    caplog.set_level(logging.DEBUG)

    @log_lifecycle
    async def sample_async(x, y):
        await asyncio.sleep(0.01)
        return x + y

    result = await sample_async(2, 3)
    assert result == 5

    logs = [rec.message for rec in caplog.records]
    assert "start: sample_async" in logs
    assert "finished: sample_async" in logs
    assert any("log type count" in msg for msg in logs)
