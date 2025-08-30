import asyncio
import os
from typing import Callable, Iterator

from tqdm import tqdm

from src.request.common import HSAccountTypes, HSType
from src.request.results import CategoryRecord, PlayerRecord
from src.util import json_wrapper
from src.util.log import get_logger

logger = get_logger()
ENCODING = "utf-8"


async def write_records(in_queue: asyncio.Queue, out_file: str, format: Callable, total: int):
    """
    Asynchronously writes records from a queue to a file.

    This coroutine reads items from an asyncio.Queue and writes them to a specified file.
    Each item is formatted using the provided formatting function before being written.
    The function writes a total number of items specified by `total`. A progress bar is 
    displayed during writing.
    """
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a', encoding=ENCODING) as f:
        for _ in tqdm(range(total), smoothing=0.01, desc=f'writing to {out_file}'):
            record = await in_queue.get()
            if record is not None:
                f.write(format(record) + '\n')


def write_record(out_file: str, data: str):
    """ Writes a single string record to a file, each record is written on a new line. """
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a', encoding=ENCODING) as f:
        f.write(data + '\n')


def read_proxies(proxy_file: str | None) -> list[str]:
    """ Reads a list of proxies from a file,e ach line in the file is treated as a separate proxy. """
    if proxy_file and os.path.isfile(proxy_file):
        with open(proxy_file, "r", encoding=ENCODING) as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    return proxies


def read_hs_records(file: str) -> Iterator[CategoryRecord]:
    """ Reads a list of category records from a file, each line in the file is treated as a separate record. """
    if not file or not os.path.isfile(file):
        return iter([])

    with open(file, "r", encoding=ENCODING) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            data = json_wrapper.from_json(line)
            try:
                yield CategoryRecord(**data)
            except Exception as e:
                logger.warning(f"Skipping invalid record in {file}: {e}")
                continue


def read_filtered_result(file: str) -> Iterator[PlayerRecord]:
    """ Reads a list of filtered records from a file, each line in the file is treated as a separate record. """
    if not file or not os.path.isfile(file):
        return iter([])

    with open(file, "r", encoding=ENCODING) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            data = json_wrapper.from_json(line)["record"]
            try:
                yield PlayerRecord.from_dict(data)
            except Exception as e:
                logger.warning(f"Skipping invalid record in {file}: {e}")
                continue


def filtered_result_formatter(job) -> str:
    """ Function for formatting `HSLookupJob` job result. """
    return json_wrapper.to_json({"rank": job.priority, "record": job.result.to_dict()})


def build_temp_file(out_file: str, account_type: HSAccountTypes, hs_type: HSType) -> str:
    """
    Constructs a temporary file name based on the original file and account/type identifiers.

    The temporary file name is created by combining the base name of `out_file` (without
    extension) with the string representations of `account_type`, `hs_type`, and the suffix
    "temp", separated by periods.
    """
    base, _ = os.path.splitext(out_file)
    return ".".join([base, str(account_type), str(hs_type), "temp"])
