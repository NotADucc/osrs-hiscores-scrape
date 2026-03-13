import datetime
import functools
import inspect
import os
import time
from typing import Callable

from src.util import mem_profile
from src.util.log import get_logger

logger = get_logger()


def benchmark(callback: Callable):
    """ Decorator that benchmarks a method by logging time spend and memory usage. """
    @functools.wraps(callback)
    async def wrapper(*args, **kwargs):
        filename = "unknown"
        start_time = end_time = None
        start_mem = end_mem = None
        result = None

        try:
            start_mem = mem_profile.memory_usage_psutil()
            start_time = time.perf_counter()

            result = callback(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result

            return result
        finally:
            try:
                end_mem = mem_profile.memory_usage_psutil()
                end_time = time.perf_counter()
                filename = os.path.basename(inspect.getfile(callback))

                if start_time is not None and start_mem is not None:
                    logger.debug(
                        f"[{filename}] - {callback.__name__} took {datetime.timedelta(seconds=end_time - start_time)} and {end_mem - start_mem:.6f} MB"
                    )
            except Exception:
                logger.error("Benchmark logging failed")
    return wrapper
