import asyncio
from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

from src.request.common import HS_PAGE_SIZE, HSAccountTypes, HSType
from src.request.dto import (GetFilteredPageRangeRequest,
                             GetMaxHighscorePageRequest)
from src.request.request import Requests
from src.request.results import CategoryRecord, PlayerRecord


class IJob(ABC):
    priority: int
    result: Any


@dataclass(order=True)
class HSCategoryJob(IJob):
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
    result: List[CategoryRecord] = None  # type: ignore


@dataclass(order=True)
class HSLookupJob(IJob):
    """
    Represents a job for looking up a player's hiscore data.

    Each job targets one username on a specific hiscore endpoint. 
    The result is populated in a `PlayerRecord` once the lookup succesfully completes.
    """
    priority: int
    username: str
    account_type: HSAccountTypes
    result: PlayerRecord = None  # type: ignore


class JobManager:
    """ A job utility class for tracking and awaiting job progress, signals when jobs are finished. """

    def __init__(self, start: int, end: int, end_inclusive: bool = True):
        self.v = start
        self.end = end
        self.end_inclusive = end_inclusive
        self.nextcalled = asyncio.Event()
        self.finished_event = asyncio.Event()

    @property
    def value(self):
        return self.v

    def is_finished(self) -> bool:
        return self.v > self.end if self.end_inclusive else self.v >= self.end

    # created incase i need it later, currently we assume that there are no gaps in priority in the Q
    # so if there is one, it would indefinitely halt
    # now you can say that it's the job of the interface user to create a correct Q
    def set(self, n):
        """ set the value to `n` and signal waiting tasks. """
        if self.is_finished():
            return
        self.v = n
        self.nextcalled.set()
        if self.is_finished():
            self.finished_event.set()

    def next(self, n=1):
        """ Increment the counter by `n` (default 1) and signal waiting tasks. """
        if self.is_finished():
            return
        self.v += n
        self.nextcalled.set()
        if self.is_finished():
            self.finished_event.set()

    async def await_next(self):
        """ Asynchronously wait until the counter is incremented, then reset the event. """
        if self.is_finished():
            return
        await self.nextcalled.wait()
        self.nextcalled.clear()

    async def await_until_finished(self):
        """Wait until the job manager reaches its end condition."""
        if self.is_finished():
            return
        await self.finished_event.wait()


JQ = TypeVar('JQ')


class JobQueue(Generic[JQ]):
    """ An asynchronous priority queue wrapper. """

    def __init__(self, maxsize=None):
        self._q = asyncio.PriorityQueue[JQ]()
        self._got = asyncio.Event()
        self._max_size = maxsize

    def __len__(self) -> int:
        return self._q.qsize()

    async def put(self, item: JQ, force=False):
        """
        Asynchronously add an item to the queue. 
        If `max_size` is set, waits until there is room unless `force=True`
        """
        if self._max_size and not force:
            while self._q.qsize() >= self._max_size:
                await self._got.wait()
                self._got.clear()
        await self._q.put(item)

    async def get(self) -> JQ:
        """
        Asynchronously remove and return the highest-priority item from the queue. 
        Triggers the `got` event to unblock `put`
        """
        item = await self._q.get()
        self._got.set()
        return item

    def peek(self) -> JQ:
        """ 
        Asynchronously return the highest-priority item from the queue without removing it. 

        Raises:
            QueueEmpty raised if Q is empty.
        """
        if self._q.empty():
            raise asyncio.QueueEmpty("peeking an empty JobQueue")
        return self._q._queue[0]  # type: ignore

    def last(self) -> JQ:
        """ 
        Asynchronously return the highest-priority item from the queue without removing it. 

        Raises:
            QueueEmpty raised if Q is empty.
        """
        if self._q.empty():
            raise asyncio.QueueEmpty(
                "cannot retrieve last item from an empty JobQueue")
        return self._q._queue[-1]  # type: ignore


async def get_hs_page_job(req: Requests, start_rank: int, end_rank: int, max_page_req: GetMaxHighscorePageRequest) -> List[HSCategoryJob]:
    """
    Generate jobs for fetching OSRS hiscore pages within a rank range.

    This function calculates which hiscore pages correspond to the given
    rank range, and retrieves the maximum available page and rank.

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    start_page, end_page = extract_page_nr_from_rank(
        start_rank=start_rank, end_rank=end_rank)

    res = await req.get_max_page(max_page_req=max_page_req)
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
                      account_type=max_page_req.account_type, hs_type=max_page_req.hs_type,
                      start_idx=(
                          start_rank - 1) % HS_PAGE_SIZE if page_num == start_page else 0,
                      end_idx=(end_rank - 1) % HS_PAGE_SIZE +
                      1 if page_num == end_rank else HS_PAGE_SIZE,
                      )
        for page_num in range(start_page, end_page + 1)
    ]


async def get_hs_filtered_job(req: Requests, start_rank: int, end_rank: int, page_range_req: GetFilteredPageRangeRequest) -> List[HSCategoryJob]:
    """
    Generate jobs for fetching OSRS hiscore pages within a rank range.

    This function calculates which hiscore pages correspond to the given
    rank range, and retrieves a range based on a given predicate.

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    start_page, end_page = extract_page_nr_from_rank(
        start_rank=start_rank, end_rank=end_rank)

    page_range = await req.get_filtered_page_range(page_range_req=page_range_req)
    filter_start_page, filter_start_rank = page_range.start_page, page_range.start_rank
    filter_end_page, filter_end_rank = page_range.end_page, page_range.end_rank

    if filter_start_rank > start_rank:
        start_page = filter_start_page
        start_rank = filter_start_rank

    if end_rank <= 0 or filter_end_rank < end_rank:
        end_page = filter_end_page
        end_rank = filter_end_rank

    if start_rank > end_rank:
        return []

    return [
        HSCategoryJob(
            priority=page_num,
            page_num=page_num,
            start_rank=start_rank if page_num == start_page
                else (page_num - 1) * HS_PAGE_SIZE + 1,  # nopep8
            end_rank=end_rank if page_num == end_page
                else (page_num - 1) * HS_PAGE_SIZE + HS_PAGE_SIZE,  # nopep8
            account_type=page_range_req.account_type,
            hs_type=page_range_req.filter_entry.hstype,
            start_idx=(start_rank - 1) % HS_PAGE_SIZE if page_num == start_page
                else 0,  # nopep8
            end_idx=(end_rank - 1) % HS_PAGE_SIZE + 1 if page_num == end_page
                else HS_PAGE_SIZE,  # nopep8
        )
        for page_num in range(start_page, end_page + 1)
    ]


def extract_page_nr_from_rank(start_rank: int, end_rank: int) -> tuple[int, int]:
    if start_rank < 1:
        raise ValueError("Start rank is smaller than 1")

    if end_rank > 0 and start_rank > end_rank:
        raise ValueError("Start rank is greater than end rank")

    start_page = (start_rank - 1) // 25 + 1
    end_page = (end_rank - 1) // 25 + 1

    return (start_page, end_page)
