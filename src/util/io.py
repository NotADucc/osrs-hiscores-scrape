import asyncio
import os
import sys
from typing import Callable, Iterator

from tqdm import tqdm

from src.request.common import HSAccountTypes, HSType
from src.request.results import CategoryRecord, PlayerRecord
from src.util import json_wrapper
from src.util.log import get_logger
from src.worker.job import HSLookupJob

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


def read_hs_records(file_path: str) -> Iterator[CategoryRecord]:
    """ Reads a list of category records from a file, each line in the file is treated as a separate record. """
    if not file_path or not os.path.isfile(file_path):
        return iter([])

    with open(file_path, "r", encoding=ENCODING) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json_wrapper.from_json(line)
                yield CategoryRecord(**data)
            except Exception as e:
                logger.warning(f"Skipping invalid record in {file_path}: {e}")
                continue


def read_filtered_result(file_path: str) -> Iterator[PlayerRecord]:
    """ Reads a list of filtered records from a file, each line in the file is treated as a separate record. """
    if not file_path or not os.path.isfile(file_path):
        return iter([])

    with open(file_path, "r", encoding=ENCODING) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json_wrapper.from_json(line)["record"]
                yield PlayerRecord.from_dict(data)
            except Exception as e:
                logger.warning(f"Skipping invalid record in {file_path}: {e}")
                continue


def filtered_result_formatter(job: HSLookupJob) -> str:
    """ Function for formatting `HSLookupJob` job result. """
    return json_wrapper.to_json({"rank": job.priority, "record": job.result.to_dict()})


def build_temp_file(file_path: str, account_type: HSAccountTypes, hs_type: HSType) -> str:
    """
    Constructs a temporary file name based on the original file, account/type identifiers and script it's currently running.

    The temporary file name is created by combining the base name of `file_path` (without
    extension) with the string representations of `account_type`, `hs_type`, current running script, and the suffix
    "temp", separated by periods.
    """
    script_name = os.path.basename(sys.argv[0])
    base_script_name, _ = os.path.splitext(script_name)

    base_file_path, _ = os.path.splitext(file_path)
    return ".".join([base_file_path, str(account_type), str(hs_type), base_script_name, "temp"])
