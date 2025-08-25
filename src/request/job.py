import asyncio
from dataclasses import dataclass
from typing import List

from src.request.common import HS_PAGE_SIZE, HSAccountTypes, HSType
from src.request.dto import GetMaxHighscorePageRequest, GetFilteredPageRangeRequest
from src.request.request import Requests
from src.request.results import CategoryRecord, PlayerRecord


@dataclass(order=True)
class HSCategoryJob:
    """
    Represents a job for fetching and processing hiscore data.

    A job corresponds to retrieving a specific page from the OSRS
    hiscores, extracting rank/username data, and enqueueing the 1-25
    usernames in rank order. Internal bookkeeping indices are used
    to simplify mapping between ranks and list slices.
    """
    priority: int
    page_num: int
    start_rank: int
    end_rank: int
    hs_type: HSType
    account_type: HSAccountTypes
    start_idx: int  # internal bookkeeping cuz i cbf working with slices and ranks
    end_idx: int  # internal bookkeeping cuz i cbf working with slices and ranks
    result: List[CategoryRecord] = None 


@dataclass(order=True)
class HSLookupJob:
    """
    Represents a job for looking up a player's hiscore data.

    Each job targets one username on a specific hiscore endpoint. 
    The result is populated in a `PlayerRecord` once the lookup succesfully completes.
    """
    priority: int
    username: str
    account_type: HSAccountTypes
    result: PlayerRecord = None 


class JobCounter:
    """ A counter utility for tracking and awaiting job progress. """

    def __init__(self, value: int):
        self.v = value
        self.nextcalled = asyncio.Event()

    @property
    def value(self):
        return self.v

    def next(self, n=1):
        """ Increment the counter by ``n`` (default 1) and signal waiting tasks. """
        self.v += n
        self.nextcalled.set()

    async def await_next(self):
        """ Asynchronously wait until the counter is incremented, then reset the event. """
        await self.nextcalled.wait()
        self.nextcalled.clear()


class JobQueue:
    """ An asynchronous priority queue. """

    def __init__(self, max_size=None):
        self.q = asyncio.PriorityQueue()
        self.got = asyncio.Event()
        self.max_size = max_size

    def __len__(self):
        return self.q.qsize()

    async def put(self, item, force=False):
        """
        Asynchronously add an item to the queue. 
        If `max_size` is set, waits until there is room unless `force=True`
        """
        if self.max_size and not force:
            while self.q.qsize() >= self.max_size:
                await self.got.wait()
                self.got.clear()
        await self.q.put(item)

    async def get(self):
        """
        Asynchronously remove and return the highest-priority item from the queue. 
        Triggers the `got` event to unblock `put`
        """
        item = await self.q.get()
        self.got.set()
        return item


async def get_hs_page_job(req: Requests, start_rank: int, end_rank: int, input: GetMaxHighscorePageRequest) -> List[HSCategoryJob]:
    """
    Generate jobs for fetching OSRS hiscore pages within a rank range.

    This function calculates which hiscore pages correspond to the given
    rank range, and retrieves the maximum available page and rank.

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    start_page = (start_rank - 1) // 25 + 1
    end_page = (end_rank - 1) // 25 + 1

    if start_rank < 1:
        raise ValueError("Start page is smaller than 1")

    if end_rank > 0 and start_rank > end_rank:
        raise ValueError("Start rank is greater than end rank")

    res = await req.get_max_page(input=input)
    max_page, max_rank = res.page_nr, res.rank_nr

    if end_rank <= 0 or end_rank >= max_rank:
        end_page = max_page
        end_rank = max_rank
    else:
        end_page = end_page
        end_rank = end_rank

    if start_rank > end_rank:
        return []

    return [
        HSCategoryJob(priority=page_num, page_num=page_num,
                      start_rank=start_rank if page_num == start_page else (
                          page_num - 1) * HS_PAGE_SIZE + 1,
                      end_rank=end_rank if page_num == end_page else (
                          page_num - 1) * HS_PAGE_SIZE + HS_PAGE_SIZE,
                      account_type=input.account_type, hs_type=input.hs_type,
                      start_idx=(
                          start_rank - 1) % HS_PAGE_SIZE if page_num == start_page else 0,
                      end_idx=(end_rank - 1) % HS_PAGE_SIZE +
                      1 if page_num == end_rank else HS_PAGE_SIZE,
                      )
        for page_num in range(start_page, end_page + 1)
    ]


async def get_hs_filtered_job(req: Requests, start_rank: int, end_rank: int, input: GetFilteredPageRangeRequest) -> List[HSCategoryJob]:
    """
    Generate jobs for fetching OSRS hiscore pages within a rank range.

    This function calculates which hiscore pages correspond to the given
    rank range, and retrieves a range based on a given predicate.

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    start_page = (start_rank - 1) // 25 + 1
    end_page = (end_rank - 1) // 25 + 1

    if start_rank < 1:
        raise ValueError("Start page is smaller than 1")

    if end_rank > 0 and start_rank > end_rank:
        raise ValueError("Start rank is greater than end rank")
    
    page_range = await req.get_filtered_page_range(input=input)
    
    if start_page < page_range.start_page:
        start_page = page_range.start_page
        start_rank = page_range.start_rank

    max_page, max_rank = page_range.end_page, page_range.end_rank

    if end_rank <= 0 or end_rank >= max_rank:
        end_page = max_page
        end_rank = max_rank
    else:
        end_page = end_page
        end_rank = end_rank

    if start_rank > end_rank:
        return []

    return [
        HSCategoryJob(priority=page_num, page_num=page_num,
                      start_rank=start_rank if page_num == start_page else (
                          page_num - 1) * HS_PAGE_SIZE + 1,
                      end_rank=end_rank if page_num == end_page else (
                          page_num - 1) * HS_PAGE_SIZE + HS_PAGE_SIZE,
                      account_type=input.account_type, hs_type=input.hs_type,
                      start_idx=(
                          start_rank - 1) % HS_PAGE_SIZE if page_num == start_page else 0,
                      end_idx=(end_rank - 1) % HS_PAGE_SIZE +
                      1 if page_num == end_rank else HS_PAGE_SIZE,
                      )
        for page_num in range(start_page, end_page + 1)
    ]
