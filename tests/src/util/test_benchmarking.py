import asyncio
import pytest
from unittest.mock import patch

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
        mock_logger.assert_called_once()
        log_msg = mock_logger.call_args[0][0]
        assert "[test_benchmarking.py] - dummy_async took 0:00:01 and 5.000000 MB" == log_msg


@pytest.mark.asyncio
async def test_benchmark_sync_function():
    def dummy_sync(x, y):
        return x + y

    with patch("src.util.mem_profile.memory_usage_psutil", side_effect=[200.0, 200.5]), \
         patch("time.perf_counter", side_effect=[10.0, 71.5]), \
         patch("src.util.log.LoggerWrapper.debug") as mock_logger:

        wrapped = benchmark(dummy_sync)
        result = await wrapped(3, 7)

        assert result == 10
        mock_logger.assert_called_once()
        log_msg = mock_logger.call_args[0][0]
        assert "[test_benchmarking.py] - dummy_sync took 0:01:01.500000 and 0.500000 MB" == log_msg