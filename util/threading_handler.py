import concurrent.futures
import functools


def spawn_threads(process, records):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process, records)
