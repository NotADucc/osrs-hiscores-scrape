import asyncio
import os
from typing import Callable, Iterator

from tqdm import tqdm

from src.request.common import HSAccountTypes, HSType
from src.request.errors import FinishedScript
from src.request.results import CategoryRecord
from src.util import json_wrapper

ENCODING = "utf-8"


async def write_records(in_queue: asyncio.Queue, out_file: str, format: Callable, total: int):
    """
    Asynchronously writes records from a queue to a file.

    This coroutine reads items from an asyncio.Queue and writes them to a specified file.
    Each item is formatted using the provided formatting function before being written.
    The function writes a total number of items specified by `total`. A progress bar is 
    displayed during writing.

    Args:
        in_queue (asyncio.Queue): The queue from which to retrieve items.
        out_file (str): Path to the output file.
        format (Callable): A function that converts a queue item into a string for writing.
        total (int): The total number of items to process from the queue.

    Raises:
        FinishedScript: Custom exception indicating that writing has finished.
    """
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a', encoding=ENCODING) as f:
        for _ in tqdm(range(total), smoothing=0.01, desc=f'writing to {out_file}'):
            job = await in_queue.get()
            if job is not None:
                f.write(format(job) + '\n')

        raise FinishedScript


def write_record(out_file: str, data: str):
    """
    Writes a single string record to a file.

    Each record is written on a new line.

    Args:
        out_file (str): Path to the output file.
        data (str): The string data to write to the file.
    """
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a', encoding=ENCODING) as f:
        f.write(data + '\n')


def read_proxies(proxy_file: str) -> list[str]:
    """
    Reads a list of proxies from a file.

    Each line in the file is treated as a separate proxy.

    Args:
        proxy_file (str): Path to the file containing proxies.

    Returns:
        list[str]: A list of proxies read from the file, or an empty list if the file
                   does not exist or is None.
    """
    if proxy_file is not None and os.path.isfile(proxy_file):
        with open(proxy_file, "r", encoding=ENCODING) as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    return proxies


def read_hs_records(file: str) -> Iterator[CategoryRecord]:
    """
    Reads a list of category records from a file.

    Each line in the file is treated as a separate record.

    Args:
        file (str): Path to the file containing category records.

    Returns:
        Iterator[CategoryRecord]: An iterator of records read from the file, or an empty iterator if the file
                   does not exist or is None.
    """
    if not os.path.isfile(file):
        return iter([])

    with open(file, "r", encoding=ENCODING) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            data = json_wrapper.from_json(line)
            yield CategoryRecord(**data)


def build_temp_file(out_file: str, account_type: HSAccountTypes, hs_type: HSType) -> str:
    """
    Constructs a temporary file name based on the original file and account/type identifiers.

    The temporary file name is created by combining the base name of `out_file` (without
    extension) with the string representations of `account_type`, `hs_type`, and the suffix
    "temp", separated by periods.

    Args:
        out_file (str): The original output file path.
        account_type (HSAccountTypes): The account type identifier.
        hs_type (HSType): The HS type identifier.

    Returns:
        str: The constructed temporary file path.
    """
    base, _ = os.path.splitext(out_file)
    return ".".join([base, str(account_type), str(hs_type), "temp"])
