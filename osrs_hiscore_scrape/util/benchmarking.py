import datetime
import functools
import inspect
import os
import time
import tracemalloc
from typing import Callable

from . import mem_profile
from .log import get_logger

logger = get_logger()


def benchmark(callback: Callable):
    """ Decorator that benchmarks a method by logging time spend and memory usage. """
    @functools.wraps(callback)
    async def wrapper(*args, **kwargs):
        filename = os.path.basename(inspect.getfile(callback))
        start_time = time.perf_counter()
        tracemalloc.start()
        start_mem = mem_profile.memory_usage_psutil()

        try:
            result = callback(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        finally:
            end_time = time.perf_counter()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            end_mem = mem_profile.memory_usage_psutil()

            logger.debug(
                f"[{filename}] - {callback.__name__} took {datetime.timedelta(seconds=end_time - start_time)}"
            )
            logger.debug(f"Python peak memory: {peak / (1024 ** 2):.6f} MB")
            logger.debug(f"OS-level memory: {end_mem - start_mem:.6f} MB")

    return wrapper
