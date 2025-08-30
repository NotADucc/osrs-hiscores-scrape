import asyncio
from asyncio import CancelledError, Queue
from gc import is_finalized
from typing import Callable, NoReturn

from src.request.common import HSType
from src.request.dto import GetHighscorePageRequest, GetPlayerRequest
from src.request.errors import NotFound, RetryFailed
from src.request.request import Requests
from src.request.results import CategoryInfo
from src.util.retry_handler import retry
from src.worker.job import (HSCategoryJob, HSLookupJob, IJob, JobManager,
                            JobQueue)


class Worker:
    """
    Represents an asynchronous worker that processes jobs from an input queue
    and forwards results to an output queue, coordinating execution via a JobCounter.

    The worker continuously fetches jobs from `in_queue`, executes a request
    function on each job, waits for its turn based on the job's priority, and
    then enqueues the result using a provided enqueue function.
    """

    def __init__(
        self,
        req: Requests,
        in_queue: JobQueue[IJob],
        out_queue: Queue[IJob] | JobQueue[IJob],
        job_manager: JobManager,
        request_fn: Callable,
        enqueue_fn: Callable,
    ):
        self.req = req
        self.in_q = in_queue
        self.out_q = out_queue
        self.job_manager = job_manager
        self.request_fn = request_fn
        self.enqueue_fn = enqueue_fn

    async def run(self, initial_delay: float = 0) -> None:
        """            
        Continuously process jobs from the input queue:
            1. Optionally wait for an initial delay.
            2. Retrieve a job from the input queue.
            3. Execute `request_fn` on the job if its result is None, with retry handling.
            4. Wait until `job_counter` reaches the job's priority.
            5. Enqueue the processed job using `enqueue_fn`.
            6. Increment the `job_counter`.

        Exceptions Handled:
            NotFound: Simply increments the job counter and continues.
            CancelledError, RetryFailed: Requeues the job forcibly and re-raises the exception.
        """
        await asyncio.sleep(initial_delay)
        while not self.job_manager.is_finished():
            done, _ = await asyncio.wait(
                [
                    asyncio.create_task(self.in_q.get()),
                    asyncio.create_task(self.job_manager.await_until_finished()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            job = next(iter(done)).result()

            if not job:
                continue

            try:
                if job.result is None:
                    await retry(self.request_fn, req=self.req, job=job)

                while self.job_manager.value < job.priority:
                    await self.job_manager.await_next()

                await self.enqueue_fn(self.out_q, job)
                self.job_manager.next()

            except NotFound:
                self.job_manager.next()
            except (CancelledError, RetryFailed):
                await self.in_q.put(job, force=True)
                raise

def create_workers(
        req: Requests,
        in_queue: JobQueue[IJob],
        out_queue: Queue[IJob] | JobQueue[IJob],
        job_manager: JobManager,
        request_fn: Callable,
        enqueue_fn: Callable,
        num_workers: int
    ):
    return [Worker(req=req, request_fn=request_fn, enqueue_fn=enqueue_fn, in_queue=in_queue, out_queue=out_queue, job_manager=job_manager)
                for _ in range(num_workers)]


async def request_hs_page(req: Requests, job: HSCategoryJob):
    """ Fetch the hiscore page for a given job and store the result in the job. """
    job.result = await req.get_hs_page(GetHighscorePageRequest(page_num=job.page_num, hs_type=job.hs_type, account_type=job.account_type))


async def request_user_stats(req: Requests, job: HSLookupJob):
    """ Fetch player stats for a given username and store the result in the job. """
    job.result = await req.get_user_stats(GetPlayerRequest(username=job.username, account_type=job.account_type))


async def enqueue_hs_page(queue: JobQueue | Queue, job: HSCategoryJob):
    """ Enqueue a processed hiscore page job into the given queue. """
    await queue.put(job)


async def enqueue_analyse_page_category(queue: JobQueue | Queue, job: HSCategoryJob, category_info: CategoryInfo):
    """
    Process a hiscore page job and add its relevant records to a category,
    then enqueue the job for further processing.
    """
    for record in job.result[job.start_idx:job.end_idx]:
        category_info.add(record=record)
    await queue.put(job)


async def enqueue_page_usernames(queue: JobQueue | Queue, job: HSCategoryJob):
    """
    Convert each record in a hiscore page job into individual HSLookupJob
    instances for username-based processing and enqueue them.
    """
    for record in job.result[job.start_idx:job.end_idx]:
        outjob = HSLookupJob(
            priority=record.rank, username=record.username, account_type=job.account_type)
        await queue.put(outjob)


async def enqueue_user_stats_filter(queue: JobQueue[IJob] | Queue[IJob], job: HSLookupJob, hs_filter: dict[HSType, Callable[[int | float], bool]]):
    """
    Enqueue a HSLookupJob if its result meets specified filter requirements;
    otherwise enqueue None to indicate the job does not match.
    """
    if job.result.meets_requirements(hs_filter):
        await queue.put(job)
    else:
        await queue.put(None)  # type: ignore
