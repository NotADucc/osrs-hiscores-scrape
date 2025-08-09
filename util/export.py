import asyncio
import os
from typing import Callable
from tqdm import tqdm
from request.errors import DoneScraping


async def export_records(in_queue: asyncio.Queue, out_file: str, format: Callable, total: int):
    exists = os.path.isfile(out_file)
    with open(out_file, mode='w' if not exists else 'a') as f:

        for _ in tqdm(range(total), smoothing=0.01):
            job = await in_queue.get()
            if isinstance(job.result, list):
                f.writelines(format(v) for v in job.result)
            else :
                f.write(format(job.result))
        
        raise DoneScraping