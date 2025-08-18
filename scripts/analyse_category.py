import argparse
import asyncio
import datetime
import sys

import aiohttp

from src.request.common import HSAccountTypes, HSType, get_default_workers_size
from src.request.dto import GetMaxHighscorePageRequest
from src.request.errors import FinishedScript
from src.request.job import (HSCategoryJob, JobCounter, JobQueue,
                             get_hs_page_job)
from src.request.request import Requests
from src.request.results import CategoryInfo
from src.request.worker import Worker, request_hs_page
from src.util.benchmarking import benchmark
from src.util.guard_clause_handler import script_running_in_cmd_guard
from src.util.io import (build_temp_file, read_hs_records, read_proxies, write_record,
                         write_records)
from src.util.log import finished_script, get_logger

logger = get_logger()


@finished_script
@benchmark
async def main(out_file: str, proxy_file: str | None, account_type: HSAccountTypes, hs_type: HSType, num_workers: int):
    category_info = CategoryInfo(
        name=hs_type.name, ts=datetime.datetime.now(datetime.timezone.utc))

    async def enqueue_hs_page(queue: asyncio.Queue, job: HSCategoryJob):
        for record in job.result[job.start_idx:job.end_idx]:
            category_info.add(record=record)
        await queue.put(job)

    temp_file = build_temp_file(out_file, account_type, hs_type)

    for record in read_hs_records(temp_file):
        category_info.add(record=record)

    start_rank = category_info.min.rank + 1 if category_info.min else 1

    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session, proxy_list=read_proxies(proxy_file))

        hs_scrape_joblist = await get_hs_page_job(req=req,
                                                  start_rank=start_rank,
                                                  end_rank=-1,
                                                  input=GetMaxHighscorePageRequest(
                                                      hs_type=hs_type, account_type=account_type)
                                                  )

        hs_scrape_q = JobQueue()
        for job in hs_scrape_joblist:
            await hs_scrape_q.put(job)

        T: list[asyncio.Task] = []
        try:
            if len(hs_scrape_q) == 0:
                logger.info("bypass scraping, temp file contains all the data")
                raise FinishedScript

            temp_export_q = asyncio.Queue()

            current_page = JobCounter(value=hs_scrape_joblist[0].page_num)
            hs_scrape_workers = [Worker(in_queue=hs_scrape_q, out_queue=temp_export_q, job_counter=current_page)
                                 for _ in range(num_workers)]

            T.append(asyncio.create_task(
                write_records(in_queue=temp_export_q,
                              out_file=temp_file,
                              total=hs_scrape_joblist[-1].page_num -
                              current_page.value + 1,
                              format=lambda job: '\n'.join(
                                  str(item) for item in job.result[job.start_idx:job.end_idx])
                              )
            ))
            for i, w in enumerate(hs_scrape_workers):
                T.append(asyncio.create_task(
                    w.run(req=req, request_fn=request_hs_page,
                          enqueue_fn=enqueue_hs_page, delay=i * 0.1)
                ))
            await asyncio.gather(*T)
        except FinishedScript:
            write_record(out_file=out_file, data=f'{category_info}')
        finally:
            for task in T:
                task.cancel()
            await asyncio.gather(*T, return_exceptions=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--account-type', required=True,
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should pull from")
    parser.add_argument('--hs-type', required=True,
                        type=HSType.from_string, choices=list(HSType), help="Hiscore category it should pull from")
    parser.add_argument('--num-workers', default=get_default_workers_size(), type=int,
                        help="Number of concurrent scraping threads")

    script_running_in_cmd_guard(parser)
    args = parser.parse_args()

    try:
        asyncio.run(main(args.out_file, args.proxy_file,
                    args.account_type, args.hs_type, args.num_workers))
    except Exception as e:
        logger.error(e)
        sys.exit(2)
