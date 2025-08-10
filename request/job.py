import asyncio
from dataclasses import dataclass
from typing import List
from request.common import HSAccountTypes, HSType
from request.dto import GetMaxHighscorePageRequest
from request.request import Requests
from request.results import CategoryRecord, PlayerRecord


@dataclass(order=True)
class HSCategoryJob:
    priority: int
    page_num: int
    hs_type: HSType
    account_type: HSAccountTypes
    result: List[CategoryRecord] = None


@dataclass(order=True)
class HSLookupJob:
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


async def get_category_job(req: Requests, start_page: int, input: GetMaxHighscorePageRequest) -> List[HSCategoryJob]:
    last_page = await req.get_max_page(input=input)
    return [
        HSCategoryJob(priority=pagenum, pagenum=pagenum,
                      account_type=input.account_type, hs_type=input.hs_type)
        for pagenum in range(start_page, last_page + 1)
    ]
