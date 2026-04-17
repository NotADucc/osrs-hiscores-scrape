import datetime
import functools
import inspect
import os
import time
import tracemalloc
from typing import Callable
import asyncio
import functools
import inspect
from typing import Any, Callable, TypeVar, cast


from ..util import mem_profile
from .logger import get_logger

logger = get_logger(__name__)


def profile_execution(callback: Callable):
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


T = TypeVar("T", bound=Callable[..., Any])


def log_lifecycle(func: T) -> T:
    """ Decorator that logs when a (async) or (sync) method has finished,
    also displays the count of logs per type.
    """
    async def message_wrapper(*args, **kwargs):
        logger = get_logger(__name__)
        try:
            logger.info(f"start: {func.__name__}")
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            return cast(T, result)
        except KeyboardInterrupt:
            raise
        finally:
            logger.debug(f"log type count: {logger.get_counts()}")
            logger.info(f"finished: {func.__name__}")

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await message_wrapper(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        return asyncio.run(message_wrapper(*args, **kwargs))

    return cast(T, async_wrapper) if inspect.iscoroutinefunction(func) \
        else cast(T, sync_wrapper)
