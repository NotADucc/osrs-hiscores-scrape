import asyncio
import inspect
from typing import Awaitable, Callable, TypeVar, cast

from src.request.errors import NotFound, RetryFailed
from src.util.log import get_logger

logger = get_logger()

T = TypeVar("T")


async def retry(callback: Callable[..., T | Awaitable[T]], max_retries: int = 10, initial_delay: int = 5, err_file: str = "error_log.err", exc_info: bool = False, **kwargs) -> T:
    """
    Retry a callable with exponential backoff on failure.

    Raises:
        NotFound: If the callable raises this exception.
        RetryFailed: If all retry attempts fail.
    """
    if max_retries <= 0:
        max_retries = 1

    potential_error = None
    retries = 1
    while retries <= max_retries:
        try:
            result = callback(**kwargs)
            if inspect.isawaitable(result):
                result = await result
            return cast(T, result)
        except NotFound as err:
            base_message = f"{err} | {err.details}"
            logger.error(base_message, exc_info=exc_info)
            potential_error = base_message
            raise
        except Exception as err:
            details = getattr(err, "details", None)
            base_message = f"{err}" + \
                (f" | {details}" if details else "") + f" | {kwargs}"
            logger.error(
                f"Attempt {retries} err: {base_message}", exc_info=exc_info)
            potential_error = base_message
        retries += 1
        await asyncio.sleep(retries * initial_delay)

    if inspect.ismethod(callback):
        cls_name = callback.__self__.__class__.__name__
        func_name = callback.__func__.__name__
        name = f"{cls_name}.{func_name}"
    else:
        name = getattr(callback, "__qualname__", str(callback))

    message = f"{potential_error},{name}"

    with open(err_file, "a") as f:
        f.write(f'{message}\n')

    logger.error(f"Max retries reached for '{message}'.")

    raise RetryFailed(message)
