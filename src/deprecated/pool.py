import asyncio
from typing import Any


async def execute(process, records, max_workers: int = 10, **kwargs: Any) -> None:
    """ wrapper to run async tasks """
    import warnings
    warnings.warn("pool.execute() is deprecated and scheduled for removal in a future version, use jobs and workers.",
                  DeprecationWarning,
                  stacklevel=2)

    semaphore = asyncio.Semaphore(max_workers)

    async def sem_task(record):
        async with semaphore:
            await process(record, **kwargs)

    tasks = [asyncio.create_task(sem_task(record)) for record in records]

    await asyncio.gather(*tasks)
