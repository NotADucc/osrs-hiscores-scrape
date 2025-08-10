import asyncio
from asyncio import Queue, CancelledError
from typing import Callable
from request.dto import GetHighscorePageRequest
from request.errors import NotFound, RequestFailed
from request.job import JobCounter, JobQueue, PlayerRecordJob, ScrapeJob
from request.request import Requests
from util.retry_handler import retry


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
            except (CancelledError, RequestFailed):
                await self.in_q.put(job, force=True)
                raise


async def request_page(req: Requests, job: ScrapeJob):
    job.result = await req.get_hs_page(input=GetHighscorePageRequest(job.page_num, job.hs_type, job.account_type))


async def enqueue_page_usernames(queue: Queue, job: ScrapeJob):
    for record in job.result:
        outjob = PlayerRecordJob(
            priority=record.rank, username=record.username, account_type=job.account_type)
        await queue.put(outjob)


async def request_stats(req: Requests, job: PlayerRecordJob):
    job.result = await req.get_user_stats(name=job.username, account_type=job.account_type)


async def enqueue_stats(queue: Queue, job: PlayerRecordJob):
    await queue.put(job.result)
