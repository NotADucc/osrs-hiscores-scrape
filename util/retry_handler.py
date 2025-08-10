import asyncio

from typing import Any, Callable
from request.errors import IsRateLimited, NotFound, RequestFailed
from util.log import get_logger

logger = get_logger()


async def retry(callback: Callable[..., Any], max_retries: int = 10, initial_delay: int = 20, out_file: str = "error_log", exc_info: bool = False, **kwargs) -> Any:
    retries = 1
    while retries <= max_retries:
        try:
            return await callback(**kwargs)
        except IsRateLimited as err:
            logger.warning(f"{err} | {err.details}", exc_info=exc_info)
        except NotFound as err:
            logger.error(f"{err} | {err.details}", exc_info=exc_info)
            raise
        except Exception as err:
            logger.warning(
                f"Attempt {retries} failed: {err} | {kwargs}", exc_info=exc_info)
        retries += 1
        await asyncio.sleep(retries * initial_delay)

    message = f"{','.join(str(v) for v in kwargs.values())},{callback}"

    with open(f"{out_file}.err", "a") as f:
        f.write(f'{message}\n')

    logger.error(f"Max retries reached for '{message}'.")

    raise RequestFailed(message)
