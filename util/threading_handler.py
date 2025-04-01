import concurrent.futures
import functools


def spawn_threads(process, records, max_workers: int = 10, **args: dict) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        new_process = functools.partial(
            process, **args) if args is not None else process
        executor.map(new_process, records)
