import asyncio
from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

from ..request.hs_types import HSAccountTypes, HSType
from ..request.records import CategoryRecord, PlayerRecord


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
    end_idx: int  # exclusive end index
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
        self._q = asyncio.PriorityQueue()
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
