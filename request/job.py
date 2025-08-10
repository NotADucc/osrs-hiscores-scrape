import asyncio
from dataclasses import dataclass
from typing import List
from request.common import HSAccountTypes, HSType
from request.results import CategoryRecord, PlayerRecord


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