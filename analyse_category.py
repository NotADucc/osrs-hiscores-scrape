import argparse
import asyncio
import datetime
import sys

import aiohttp

from request.dto import GetMaxHighscorePageRequest
from request.errors import FinishedScript
from request.job import JobCounter, JobQueue, get_hs_page_job
from request.request import Requests
from request.results import CategoryInfo
from request.worker import Worker, enqueue_hs_page, request_hs_page
from util.guard_clause_handler import running_script_not_in_cmd_guard
from request.common import HSType, HSAccountTypes, get_default_workers_size
from util.io import read_hs_records, read_proxies, write_records
from util.log import get_logger

logger = get_logger()

async def main(out_file: str, proxy_file: str | None, account_type: HSAccountTypes, hs_type: HSType, num_workers: int):
    category_info = CategoryInfo(
        name=hs_type.name, ts=datetime.datetime.now(datetime.timezone.utc))
    
    temp_file = ".".join([out_file.split('.')[0], str(account_type), str(hs_type), "temp"])

    temp_records = read_hs_records(temp_file)

    for record in temp_records:
        category_info.add(record=record)

    async with aiohttp.ClientSession() as session:
        req = Requests(session=session, proxy_list=read_proxies(proxy_file))

        hs_scrape_joblist = await get_hs_page_job(req=req,
                                                  start_page=1,
                                                  end_page=-1,
                                                  input=GetMaxHighscorePageRequest(
                                                      hs_type=hs_type, account_type=account_type)
                                                  )
        hs_scrape_q = JobQueue()
        for job in hs_scrape_joblist:
            await hs_scrape_q.put(job)

        export_q = asyncio.Queue()

        current_page = JobCounter(value=hs_scrape_joblist[0].page_num)
        hs_scrape_workers = [Worker(in_queue=hs_scrape_q, out_queue=export_q, job_counter=current_page)
                             for _ in range(num_workers)]

        T = [asyncio.create_task(
            write_records(in_queue=export_q,
                          out_file=temp_file,
                          total=hs_scrape_joblist[-1].page_num -
                          current_page.value + 1,
                          format=lambda job: '\n'.join(
                              str(item) for item in job.result)
                          )
        )]
        for w in hs_scrape_workers:
            T.append(asyncio.create_task(
                w.run(req=req, request_fn=request_hs_page,
                      enqueue_fn=enqueue_hs_page)
            ))
        try:
            await asyncio.gather(*T)
        except FinishedScript:
            pass
        finally:
            for task in T:
                task.cancel()
            await asyncio.gather(*T, return_exceptions=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--account-type', 
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should pull from")
    parser.add_argument('--hs-type', required=True,
                        type=HSType.from_string, choices=list(HSType), help="Hiscore category it should pull from")
    parser.add_argument('--num-workers', default=get_default_workers_size(), type=int,
                        help="Number of concurrent scraping threads")
    
    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    try:
        asyncio.run(main(args.out_file, args.proxy_file, args.account_type, args.hs_type, args.num_works))
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    
    logger.info("done")
    sys.exit(0)
