import asyncio
from asyncio import Queue, CancelledError
from dataclasses import dataclass
from typing import Callable, List
from request.common import HSAccountTypes, HSType
from request.dto import GetHighscorePageRequest
from request.errors import NotFound, RequestFailed
from request.request import Requests
from request.results import CategoryRecord, PlayerRecord
from util.retry_handler import retry


@dataclass(order=True)
class ScrapeJob:
    priority: int
    page_num: int
    hs_type: HSType
    account_type: HSAccountTypes
    result: List[CategoryRecord] = None


@dataclass(order=True)
class PlayerRecordJob:
    priority: int
    username: str
    account_type: HSAccountTypes
    result: PlayerRecord = None


class JobCounter:
    def __init__(self, value: int):
        self.v = value
        self.nextcalled = asyncio.Event()

    @property
    def value(self):
        return self.v

    def next(self, n=1):
        self.v += n
        self.nextcalled.set()

    async def await_next(self):
        await self.nextcalled.wait()
        self.nextcalled.clear()


class JobQueue:
    def __init__(self, max_size=None):
        self.q = asyncio.PriorityQueue()
        self.got = asyncio.Event()
        self.max_size = max_size

    async def put(self, item, force=False):
        if self.max_size and not force:
            while self.q.qsize() >= self.max_size:
                await self.got.wait()
                self.got.clear()
        await self.q.put(item)

    async def get(self):
        item = await self.q.get()
        self.got.set()
        return item


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
