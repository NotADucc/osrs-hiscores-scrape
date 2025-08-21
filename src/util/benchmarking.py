import functools
import inspect
import time
from typing import Callable

from src.util import mem_profile
from src.util.log import get_logger

logger = get_logger()


def benchmark(callback: Callable):
    """
        Decorator that benchmarks a method by logging time spend and memory usage.

        Args:
            callback (Callable): The method that needs benchmarking.

        Returns:
            Callable: An asynchronous wrapper coroutine
    """

    @functools.wraps(callback)
    async def wrapper(*args, **kwargs):
        start_mem = mem_profile.memory_usage_psutil()
        start_time = time.perf_counter()

        result = callback(*args, **kwargs)
        if inspect.isawaitable(result):
            result = await result

        end_mem = mem_profile.memory_usage_psutil()
        end_time = time.perf_counter()

        logger.info(
            f"{callback.__name__} took {end_time - start_time:.4f} seconds and {end_mem - start_mem:.6f} MB")
        return result
    return wrapper
