import threading

from time import sleep
from typing import Any, Callable
from request.common import IsRateLimited, PlayerDoesNotExist
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def retry(callback: Callable[..., Any], max_retries: int = 10, initial_delay: int = 30, out_file: str = "error_log", exc_info: bool = False, **kwargs) -> Any:
    retries = 1
    while retries <= max_retries:
        try:
            return callback(**kwargs)
        except IsRateLimited as err:
            logger.error(f"{err} | {err.details}", exc_info=exc_info)
        except PlayerDoesNotExist as err:
            logger.error(f"{err} | {err.details}", exc_info=exc_info)
            return None
        except Exception as err:
            logger.error(
                f"Attempt {retries} failed: {err} | {kwargs}", exc_info=exc_info)
        retries += 1
        sleep(retries * initial_delay)

    message = f"{','.join(str(v) for v in kwargs.values())},{callback}"

    with file_lock:
        with open(f"{out_file}.err", "a") as f:
            f.write(f'{message}\n')
    logger.error(f"Max retries reached for '{message}'.")

    return None
