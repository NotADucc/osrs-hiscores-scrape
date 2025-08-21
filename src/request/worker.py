import asyncio
from asyncio import CancelledError, Queue
from typing import Callable

from src.request.common import HSType
from src.request.dto import GetHighscorePageRequest, GetPlayerRequest
from src.request.errors import NotFound, RetryFailed
from src.request.job import HSCategoryJob, HSLookupJob, JobCounter, JobQueue
from src.request.request import Requests
from src.request.results import CategoryInfo
from src.util.retry_handler import retry


class Worker:
    """
    Represents an asynchronous worker that processes jobs from an input queue
    and forwards results to an output queue, coordinating execution via a JobCounter.

    The worker continuously fetches jobs from `in_queue`, executes a request
    function on each job, waits for its turn based on the job's priority, and
    then enqueues the result using a provided enqueue function.

    Attributes:
        in_q (JobQueue): The input queue containing jobs to process.
        out_q (Queue): The output queue where processed jobs/results are placed.
        job_counter (JobCounter): Tracks the current priority and controls
            job execution order.

    Exceptions Handled:
        NotFound: Simply increments the job counter and continues.
        CancelledError, RetryFailed: Requeues the job forcibly and re-raises the exception.
    """

    def __init__(self, in_queue: JobQueue, out_queue: Queue, job_counter: JobCounter):
        self.in_q = in_queue
        self.out_q = out_queue
        self.job_counter = job_counter

    async def run(self, req: Requests, request_fn: Callable, enqueue_fn: Callable, delay: float = 0):
        """            
        Continuously process jobs from the input queue:
            1. Optionally wait for an initial delay.
            2. Retrieve a job from the input queue.
            3. Execute `request_fn` on the job if its result is None, with retry handling.
            4. Wait until `job_counter` reaches the job's priority.
            5. Enqueue the processed job using `enqueue_fn`.
            6. Increment the `job_counter`.
        """
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
    """
    Fetch the hiscore page for a given job and store the result in the job.

    Args:
        req (Requests): An instance capable of performing hiscore requests.
        job (HSCategoryJob): The job containing page number, hiscore type,
            and account type. The fetched result is stored in `job.result`.
    """
    job.result = await req.get_hs_page(GetHighscorePageRequest(page_num=job.page_num, hs_type=job.hs_type, account_type=job.account_type))


async def request_user_stats(req: Requests, job: HSLookupJob):
    """
    Fetch player stats for a given username and store the result in the job.

    Args:
        req (Requests): An instance capable of performing player stat requests.
        job (HSLookupJob): The job containing the username and account type.
            The fetched result is stored in `job.result`.
    """
    job.result = await req.get_user_stats(GetPlayerRequest(username=job.username, account_type=job.account_type))


async def enqueue_hs_page(queue: JobQueue | Queue, job: HSCategoryJob):
    """
    Enqueue a processed hiscore page job into the given queue.

    Args:
        queue (JobQueue | Queue): The output queue to put the job into.
        job (HSCategoryJob): The job to enqueue.
    """
    await queue.put(job)


async def enqueue_analyse_page_category(queue: JobQueue | Queue, job: HSCategoryJob, category_info: CategoryInfo):
    """
    Process a hiscore page job and add its relevant records to a category,
    then enqueue the job for further processing.

    Args:
        queue (JobQueue | Queue): Queue to put the processed job into.
        job (HSCategoryJob): The job containing the page results to analyse.
        category_info (CategoryInfo): Object to collect the relevant records
            from the job. Only records from `start_idx` to `end_idx` are added.
    """
    for record in job.result[job.start_idx:job.end_idx]:
        category_info.add(record=record)
    await queue.put(job)


async def enqueue_page_usernames(queue: JobQueue | Queue, job: HSCategoryJob):
    """
    Convert each record in a hiscore page job into individual HSLookupJob
    instances for username-based processing and enqueue them.

    Args:
        queue (JobQueue | Queue): Queue to put the generated HSLookupJob instances into.
        job (HSCategoryJob): The job containing the page results to process.
            Only records from `start_idx` to `end_idx` are converted.
    """
    for record in job.result[job.start_idx:job.end_idx]:
        outjob = HSLookupJob(
            priority=record.rank, username=record.username, account_type=job.account_type)
        await queue.put(outjob)


async def enqueue_user_stats_filter(queue: JobQueue | Queue, job: HSLookupJob, filter: dict[HSType, int]):
    """
    Enqueue a HSLookupJob if its result meets specified filter requirements;
    otherwise enqueue None to indicate the job does not match.

    Args:
        queue (JobQueue | Queue): Queue to put the filtered job into.
        job (HSLookupJob): The job containing the player's stats to check.
        filter (dict[HSType, int]): Dictionary mapping HSTypes to minimum
            values required for the job to pass the filter.
    """
    if job.result.meets_requirements(filter):
        await queue.put(job)
    else:
        await queue.put(None)
