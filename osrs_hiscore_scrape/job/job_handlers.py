from asyncio import Queue

from ..request.dto import (GetHighscorePageRequest, GetPlayerRequest,
                           HSFilterEntry)
from ..request.records import CategoryInfo
from ..request.request import Requests
from .records import HSCategoryJob, HSLookupJob, IJob, JobQueue


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


async def enqueue_user_stats_filter(queue: JobQueue[IJob] | Queue[IJob], job: HSLookupJob, hs_filter: list[HSFilterEntry]):
    """
    Enqueue a HSLookupJob if its result meets specified filter requirements;
    otherwise enqueue None to indicate the job does not match.
    """
    if job.result.meets_requirements(hs_filter):
        await queue.put(job)
    else:
        await queue.put(None)  # type: ignore
