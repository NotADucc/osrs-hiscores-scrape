import argparse
import asyncio
import sys

import aiohttp

from src.request.common import DEFAULT_WORKER_SIZE, HSAccountTypes, HSType
from src.request.dto import GetMaxHighscorePageRequest
from src.request.errors import FinishedScript
from src.request.request import Requests
from src.util.benchmarking import benchmark
from src.util.guard_clause_handler import script_running_in_cmd_guard
from src.util.io import read_proxies, write_records
from src.util.log import finished_script, get_logger
from src.worker.job import IJob, JobManager, JobQueue, get_hs_page_job
from src.worker.worker import Worker, create_workers, enqueue_hs_page, request_hs_page

logger = get_logger()


@finished_script
@benchmark
async def main(out_file: str, proxy_file: str | None, account_type: HSAccountTypes, hs_type: HSType, start_rank: int, end_rank: int, num_workers: int):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session, proxy_list=read_proxies(proxy_file))

        hs_scrape_joblist = await get_hs_page_job(req=req,
                                                  start_rank=start_rank,
                                                  end_rank=end_rank,
                                                  input=GetMaxHighscorePageRequest(
                                                      hs_type=hs_type, account_type=account_type)
                                                  )
        hs_scrape_job_q = JobQueue[IJob]()
        for job in hs_scrape_joblist:
            await hs_scrape_job_q.put(job)

        export_q = asyncio.Queue()

        scrape_job_manager = JobManager(start=hs_scrape_joblist[0].page_num, end=hs_scrape_joblist[-1].page_num)
        hs_scrape_workers = create_workers(        
                req=req,
                in_queue=hs_scrape_job_q,
                out_queue=export_q,
                job_manager=scrape_job_manager,
                request_fn=request_hs_page,
                enqueue_fn=enqueue_hs_page,
                num_workers=num_workers
            )

        T: list[asyncio.Task[None]] = [asyncio.create_task(
            write_records(in_queue=export_q,
                          out_file=out_file,
                          total=hs_scrape_joblist[-1].page_num -
                          hs_scrape_joblist[0].page_num + 1,
                          format=lambda job: '\n'.join(
                              str(item) for item in job.result[job.start_idx:job.end_idx])
                          )
        )]
        for i, w in enumerate(hs_scrape_workers):
            T.append(asyncio.create_task(w.run(initial_delay=i * 0.1)))
        try:
            await asyncio.gather(*T)
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
    parser.add_argument('--rank-start', default=1, type=int,
                        help="Hiscore rank number it should start at (default: 1)")
    parser.add_argument('--rank-end', default=-1, type=int,
                        help="Hiscore rank number it should end at (default: end of category)")
    parser.add_argument('--num-workers', default=DEFAULT_WORKER_SIZE, type=int,
                        help="Number of concurrent scraping threads (default: 15)")

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.out_file, args.proxy_file,
                         args.account_type, args.hs_type, args.rank_start, args.rank_end, args.num_workers))
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)
