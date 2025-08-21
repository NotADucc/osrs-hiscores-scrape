import asyncio
import inspect
from typing import Any, Callable

from src.request.errors import NotFound, RetryFailed
from src.util.log import get_logger

logger = get_logger()


async def retry(callback: Callable[..., Any], max_retries: int = 10, initial_delay: int = 5, out_file: str = "error_log", exc_info: bool = False, **kwargs) -> Any | None:
    """
    Retry a callable with exponential backoff on failure.

    Args:
        callback: Function or coroutine to execute.
        max_retries: Max retry attempts (default 10).
        initial_delay: Base delay in seconds between retries (default 5).
        out_file: Prefix for logging failed attempts (default "error_log").
        exc_info: Include exception info in logs (default False).
        **kwargs: Arguments to pass to the callback.

    Returns:
        Result of `callback` if successful.

    Raises:
        NotFound: If the callable raises this exception.
        RetryFailed: If all retry attempts fail.
    """
    
    retries = 1
    while retries <= max_retries:
        try:
            result = callback(**kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        except NotFound as err:
            logger.error(f"{err} | {err.details}", exc_info=exc_info)
            raise
        except Exception as err:
            warning_mess = f"Attempt {retries} err: {err} | {err.details}" \
                if err.details else f"Attempt {retries} err: {err}"
            logger.error(f"{warning_mess} | {kwargs}", exc_info=exc_info)
        retries += 1
        await asyncio.sleep(retries * initial_delay)

    message = f"{','.join(str(v) for v in kwargs.values())},{callback}"

    with open(f"{out_file}.err", "a") as f:
        f.write(f'{message}\n')

    logger.error(f"Max retries reached for '{message}'.")

    raise RetryFailed(message)
