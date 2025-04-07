import threading

from time import sleep
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def retry(callback, *args, max_retries: int = 50, initial_delay: int = 10, out_file: str = "error_log") -> None:
    retries = 1
    while retries <= max_retries:
        try:
            return callback(*args)
        except Exception as err:
            logger.error(f"Attempt {retries} failed: {err}", exc_info=True)
            sleep(retries * initial_delay)
            retries += 1

    message = f"{','.join(map(str, args))} - {callback}"

    with file_lock:
        with open(f"{out_file}.err", "a") as f:
            f.write(f'{message}\n')
    logger.error(f"Max retries reached for '{message}'.")
