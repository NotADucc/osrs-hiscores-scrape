import asyncio
from unittest.mock import patch

import pytest

from src.util.benchmarking import benchmark


@pytest.mark.asyncio
async def test_benchmark_async_function():
    async def dummy_async(x):
        await asyncio.sleep(0.01)
        return x * 2

    with patch("src.util.mem_profile.memory_usage_psutil", side_effect=[100.0, 105.0]), \
            patch("time.perf_counter", side_effect=[1.0, 2.0]), \
            patch("src.util.log.LoggerWrapper.debug") as mock_logger:

        wrapped = benchmark(dummy_async)
        result = await wrapped(5)

        assert result == 10

        assert mock_logger.call_count == 3

        calls = [call[0][0] for call in mock_logger.call_args_list]

        assert "[test_benchmarking.py] - dummy_async took 0:00:01" in calls[0]
        assert "Python peak memory:" in calls[1]
        assert "OS-level memory: 5.000000 MB" in calls[2]


@pytest.mark.asyncio
async def test_benchmark_sync_function():
    def dummy_sync(x):
        return x * 2

    with patch("src.util.mem_profile.memory_usage_psutil", side_effect=[100.0, 105.0]), \
            patch("time.perf_counter", side_effect=[1.0, 2.0]), \
            patch("src.util.log.LoggerWrapper.debug") as mock_logger:

        wrapped = benchmark(dummy_sync)
        result = await wrapped(5)

        assert result == 10

        assert mock_logger.call_count == 3

        calls = [call[0][0] for call in mock_logger.call_args_list]

        assert "[test_benchmarking.py] - dummy_sync took 0:00:01" in calls[0]
        assert "Python peak memory:" in calls[1]
        assert "OS-level memory: 5.000000 MB" in calls[2]
