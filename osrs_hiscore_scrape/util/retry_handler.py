import asyncio
import inspect
from typing import Awaitable, Callable, TypeVar, cast

from ..exception.records import NotFound, RetryFailed
from ..log.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def _log_error(message: str, exc_info: bool, suppress: bool) -> None:
    if not suppress:
        logger.error(message, exc_info=exc_info)


def _get_callable_name(callback: Callable) -> str:
    if inspect.ismethod(callback):
        return f"{callback.__self__.__class__.__name__}.{callback.__func__.__name__}"
    return getattr(callback, "__qualname__", str(callback))


async def retry(callback: Callable[..., T | Awaitable[T]], max_retries: int = 10, initial_delay: int = 5, err_file: str = "error_log.err", exc_info: bool = False, suppress_logger: bool = False, **kwargs) -> T:
    """
    Retry a callable with exponential backoff on failure.

    Raises:
        NotFound: If the callable raises this exception.
        RetryFailed: If all retry attempts fail.
    """
    max_retries = 1 if max_retries <= 0 else max_retries

    last_error: str | None = None
    for attempt in range(1, max_retries + 1):
        try:
            result = callback(**kwargs)
            if inspect.isawaitable(result):
                result = await result
            return cast(T, result)

        except NotFound as err:
            message = f"{err} | {err.details}"
            _log_error(message, exc_info, suppress_logger)
            raise

        except Exception as err:
            details = getattr(err, "details", None)
            message = f"{err}" + (f" | {details}" if details else "") + f" | {kwargs}"

            _log_error(f"Attempt {attempt} failed: {message}", exc_info, suppress_logger)
            last_error = message

        await asyncio.sleep(attempt * initial_delay)

    name = _get_callable_name(callback)
    final_message = f"{last_error},{name}"

    with open(err_file, "a", encoding="utf-8") as f:
        f.write(final_message + "\n")

    _log_error(f"Max retries reached for '{final_message}'.", exc_info, suppress_logger)

    raise RetryFailed(final_message)


