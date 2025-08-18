import asyncio
from asyncio import CancelledError, Queue
from typing import Callable

from src.request.dto import GetHighscorePageRequest, GetPlayerRequest
from src.request.errors import NotFound, RetryFailed
from src.request.job import HSCategoryJob, HSLookupJob, JobCounter, JobQueue
from src.request.request import Requests
from src.util.retry_handler import retry


class Worker:
    def __init__(self, in_queue: JobQueue, out_queue: Queue, job_counter: JobCounter):
        self.in_q = in_queue
        self.out_q = out_queue
        self.job_counter = job_counter

    async def run(self, req: Requests, request_fn: Callable, enqueue_fn: Callable, delay: float = 0):
        await asyncio.sleep(delay)
        while True:
            job = await self.in_q.get()
            try:
                if job.result is None:
                    await retry(request_fn, req=req, job=job)

                while self.job_counter.v < job.priority:
                    await self.job_counter.await_next()

                await enqueue_fn(self.out_q, job)
                self.job_counter.next()

            except NotFound:
                self.job_counter.next()
            except (CancelledError, RetryFailed):
                await self.in_q.put(job, force=True)
                raise


async def request_hs_page(req: Requests, job: HSCategoryJob):
    job.result = await req.get_hs_page(GetHighscorePageRequest(page_num=job.page_num, hs_type=job.hs_type, account_type=job.account_type))


async def request_user_stats(req: Requests, job: HSLookupJob):
    job.result = await req.get_user_stats(GetPlayerRequest(username=job.username, account_type=job.account_type))


async def enqueue_hs_page(queue: Queue, job: HSCategoryJob):
    await queue.put(job)


async def enqueue_page_usernames(queue: Queue, job: HSCategoryJob):
    for record in job.result[job.start_idx:job.end_idx]:
        outjob = HSLookupJob(
            priority=record.rank, username=record.username, account_type=job.account_type)
        await queue.put(outjob)
