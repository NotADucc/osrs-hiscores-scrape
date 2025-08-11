import asyncio
from dataclasses import dataclass
from typing import List

from request.common import HSAccountTypes, HSType, get_page_size
from request.dto import GetMaxHighscorePageRequest
from request.request import Requests
from request.results import CategoryRecord, PlayerRecord


@dataclass(order=True)
class HSCategoryJob:
    priority: int
    page_num: int
    start_rank: int
    end_rank: int
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


async def get_hs_page_job(req: Requests, start_page: int, end_page: int, input: GetMaxHighscorePageRequest) -> List[HSCategoryJob]:
    max_page_result = await req.get_max_page(input=input)
    max_page = max_page_result.page_nr
    PAGE_SIZE = get_page_size()
    if end_page <= 0 or end_page >= max_page:
        end_page = max_page
        end_rank = max_page_result.rank_nr
    else :
        end_page = end_page
        end_rank = end_page * PAGE_SIZE

    if start_page < 1:
        raise ValueError("Start page is smaller than 1")

    if start_page > end_page:
        raise ValueError("Start page is greater than end page")

    return [
        HSCategoryJob(priority=page_num, page_num=page_num, 
                      start_rank=(page_num - 1) * PAGE_SIZE + 1, 
                      end_rank=page_num if page_num != end_page else end_rank,
                      account_type=input.account_type, hs_type=input.hs_type)
        for page_num in range(start_page, end_page + 1)
    ]

# async def transform_into_hs_page_job(req: Requests, start_page: int, end_page: int, input: GetMaxHighscorePageRequest) -> List[HSCategoryJob]:
#     max_page = await req.get_max_page(input=input)
#     end_page = max_page if end_page <= 0 or end_page >= max_page else end_page

#     if start_page < 1:
#         raise ValueError("Start page is smaller than 1")

#     if start_page > end_page:
#         raise ValueError("Start page is greater than end page")

#     return [
#         HSCategoryJob(priority=page_num, page_num=page_num,
#                       account_type=input.account_type, hs_type=input.hs_type)
#         for page_num in range(start_page, end_page + 1)
#     ]