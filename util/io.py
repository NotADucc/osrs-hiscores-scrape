import asyncio
import json
import os
from typing import Callable

from tqdm import tqdm

from request.errors import FinishedScript
from request.results import CategoryRecord


async def write_records(in_queue: asyncio.Queue, out_file: str, format: Callable, total: int):
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a') as f:
        for _ in tqdm(range(total), smoothing=0.01):
            job = await in_queue.get()
            if job is not None:
                f.write(format(job) + '\n')

        raise FinishedScript

def write_record(out_file: str, data: str):
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a') as f:
        f.write(data + '\n')

def read_proxies(proxy_file: str) -> list[str]:
    if proxy_file is not None and os.path.isfile(proxy_file):
        with open(proxy_file, "r") as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    return proxies


def read_hs_records(file: str) -> list[CategoryRecord]: 
    hs_records = [] 

    if not os.path.isfile(file):
        return hs_records
    
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue

            data = json.loads(line)
            record = CategoryRecord(**data)
            hs_records.append(record)

    return hs_records
