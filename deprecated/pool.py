import asyncio


async def execute(process, records, max_workers: int = 10, **args: dict) -> None:
    semaphore = asyncio.Semaphore(max_workers) 

    async def sem_task(record):
        async with semaphore:
            await process(record, **args)

    tasks = [asyncio.create_task(sem_task(record)) for record in records]

    await asyncio.gather(*tasks)
