import argparse
import asyncio
import sys

import aiohttp

from request.common import HSAccountTypes, HSType
from request.dto import GetMaxHighscorePageRequest
from request.errors import FinishedScript
from request.job import JobCounter, JobQueue, get_category_job
from request.request import Requests
from request.worker import Worker, enqueue_hs_page, request_hs_page
from util.export import export_records
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.log import get_logger

logger = get_logger()


async def main(out_file: str, proxy_file: str | None, account_type: HSAccountTypes, hs_type: HSType, start_page_nr: int, end_page_nr: int, num_workers: int):
    if proxy_file is not None:
        with open(proxy_file, "r") as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    async with aiohttp.ClientSession() as session:
        req = Requests(session=session, proxy_list=proxies)

        category_joblist = await get_category_job(req=req,
                                                  start_page=start_page_nr,
                                                  end_page=end_page_nr,
                                                  input=GetMaxHighscorePageRequest(
                                                      hs_type=hs_type, account_type=account_type)
                                                  )
        category_q = JobQueue()
        for job in category_joblist:
            await category_q.put(job)

        export_q = asyncio.Queue()

        current_page = JobCounter(value=category_joblist[0].page_num)
        category_workers = [Worker(in_queue=category_q, out_queue=export_q, job_counter=current_page)
                            for _ in range(num_workers)]

        T = [asyncio.create_task(
            export_records(in_queue=export_q,
                           out_file=out_file,
                           total=category_joblist[-1].page_num -
                           current_page.value + 1,
                           format=lambda lookup_job: str(lookup_job) + '\n'
                           )
        )]
        for w in category_workers:
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
    parser.add_argument('--account-type', default='regular',
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should pull from (default: 'regular')")
    parser.add_argument('--hs-type', default='overall',
                        type=HSType.from_string, choices=list(HSType), help="Hiscore category it should pull from (default: 'overall')")
    parser.add_argument('--start-page-nr', default=1, type=int,
                        help="Hiscore page number it should start at")
    parser.add_argument('--end-page-nr', default=-1, type=int,
                        help="Hiscore page number it should end at")
    parser.add_argument('--num-workers', default=50, type=int,
                        help="Number of concurrent scraping threads")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    try:
        asyncio.run(main(args.out_file, args.proxy_file,
                         args.account_type, args.hs_type, args.start_page_nr, args.end_page_nr, args.num_workers))
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    logger.info("done")
    sys.exit(0)
